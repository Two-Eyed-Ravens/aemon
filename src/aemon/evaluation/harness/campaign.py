"""Bounded offline recovery selection, provisional until independent quality review."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aemon.common.paths import ROOT
from aemon.evaluation.harness.__main__ import tree_digest
from aemon.evaluation.harness.candidate import Candidate, load_candidate
from aemon.evaluation.harness.runner import select_cases
from aemon.evaluation.harness.runtime import ModelReceipt, RuntimeExpectation

# The six guards of the evaluated configuration (test set 3's arm A).
BASE_FEATURES = frozenset(('no_repeats', 'quote_menu', 'resample_repeats', 'budget', 'grounded_beliefs', 'evidence_first'))


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class Protocol(StrictModel):
    version: Literal[1]
    baseline: str
    candidates: tuple[str, str, str]
    training_cases: tuple[str, ...] = Field(min_length=6, max_length=6)
    validation_cases: tuple[str, ...] = Field(min_length=15, max_length=15)
    first_attempt: Literal[7]
    training_attempts: Literal[1]
    validation_attempts: Literal[3]

    @model_validator(mode='after')
    def distinct_inputs(self) -> Protocol:
        paths = (self.baseline, *self.candidates)
        if len(set(paths)) != 4 or any(Path(path).is_absolute() or '..' in Path(path).parts for path in paths):
            raise ValueError('provide four distinct relative configuration paths')
        select_cases(list(self.training_cases), 'training')
        select_cases(list(self.validation_cases), 'validation')
        return self


class Snapshot(StrictModel):
    source_sha256: str
    tests_sha256: str
    data_sha256: str


class Manifest(StrictModel):
    version: Literal[1] = 1
    protocol: Protocol
    protocol_sha256: str
    baseline: Candidate
    candidates: tuple[Candidate, ...]
    snapshot: Snapshot
    runtime: str
    expectation: RuntimeExpectation
    receipt: ModelReceipt | None
    model_kind: str
    training_episodes: int = 36
    validation_episodes: int = 90
    provisional: bool = True
    quality_review: Literal['pending'] = 'pending'


class Metrics(StrictModel):
    episodes: int
    finished: int
    validated: int
    synthetic_citation_refusals: int
    total_tokens: int
    calls: int


class Comparison(StrictModel):
    name: str
    baseline: Metrics
    candidate: Metrics
    eligible: bool


class Selection(StrictModel):
    selected: str
    eligible: tuple[str, ...]
    rejected: tuple[str, ...]
    comparisons: tuple[Comparison, ...]
    reason: Literal['efficiency_improvement', 'no_improvement']
    validation: Literal['pending', 'skipped_no_eligible_candidate']
    provisional: bool = True
    quality_review: Literal['pending'] = 'pending'


class State(StrictModel):
    state: Literal['partial', 'complete']
    selected: str | None = None
    validation: Literal['pending', 'complete', 'skipped_no_eligible_candidate'] = 'pending'
    provisional: bool = True
    quality_review: Literal['pending'] = 'pending'


class Call(BaseModel):
    accepted: bool
    category: str | None = None


class Record(BaseModel):
    calls: tuple[Call, ...]


class EpisodeRow(BaseModel):
    kind: Literal['episode']
    case: str
    attempt: int
    arm: Literal['baseline', 'candidate']
    candidate_sha256: str
    finished: bool
    guards_cleared: bool
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    record: Record


class Row(BaseModel):
    kind: Literal['manifest', 'episode', 'complete']
    pairs: int | None = None


def snapshot() -> Snapshot:
    return Snapshot(
        source_sha256=tree_digest(ROOT / 'src', '*.py'),
        tests_sha256=tree_digest(ROOT / 'tests', '*.py'),
        data_sha256=tree_digest(ROOT / 'data' / 'dossier', '*.json'),
    )


def write_json(path: Path, model: BaseModel) -> None:
    with path.open('x') as stream:
        stream.write(model.model_dump_json(indent=2) + '\n')


def configurations(protocol: Protocol, directory: Path) -> tuple[Candidate, tuple[Candidate, ...]]:
    baseline = load_candidate(directory / protocol.baseline)
    candidates = tuple(load_candidate(directory / path) for path in protocol.candidates)
    if frozenset(baseline.features) != BASE_FEATURES:
        raise ValueError('baseline must contain exactly the six fixed guards')
    expected = {BASE_FEATURES | {'mask_rereads'}, BASE_FEATURES | {'progress'}, BASE_FEATURES | {'mask_rereads', 'progress'}}
    if {frozenset(candidate.features) for candidate in candidates} != expected:
        raise ValueError('candidates must be exactly baseline plus rereads, progress, and both')
    if len({baseline.name, *(candidate.name for candidate in candidates)}) != 4:
        raise ValueError('configuration names must be distinct')
    return baseline, candidates


def metrics(episodes: list[EpisodeRow]) -> Metrics:
    return Metrics(
        episodes=len(episodes),
        finished=sum(episode.finished for episode in episodes),
        validated=sum(episode.finished and episode.guards_cleared for episode in episodes),
        synthetic_citation_refusals=sum(
            not call.accepted and call.category == 'synthetic_as_evidence' for episode in episodes for call in episode.record.calls
        ),
        total_tokens=sum(episode.prompt_tokens + episode.completion_tokens for episode in episodes),
        calls=sum(len(episode.record.calls) for episode in episodes),
    )


def compare(name: str, baseline: Metrics, candidate: Metrics) -> Comparison:
    eligible = (
        candidate.finished >= baseline.finished
        and candidate.validated >= baseline.validated
        and candidate.synthetic_citation_refusals <= baseline.synthetic_citation_refusals
        and candidate.total_tokens <= baseline.total_tokens
        and (candidate.total_tokens < baseline.total_tokens or candidate.calls < baseline.calls)
    )
    return Comparison(name=name, baseline=baseline, candidate=candidate, eligible=eligible)


def choose(baseline: str, comparisons: tuple[Comparison, ...]) -> Selection:
    eligible = sorted(
        (comparison for comparison in comparisons if comparison.eligible),
        key=lambda comparison: (comparison.candidate.total_tokens, comparison.candidate.calls, comparison.name),
    )
    return Selection(
        selected=eligible[0].name if eligible else baseline,
        eligible=tuple(comparison.name for comparison in eligible),
        rejected=tuple(comparison.name for comparison in comparisons if not comparison.eligible),
        comparisons=comparisons,
        reason='efficiency_improvement' if eligible else 'no_improvement',
        validation='pending' if eligible else 'skipped_no_eligible_candidate',
    )


def read_comparison(path: Path, candidate: Candidate, baseline: Candidate, cases: tuple[str, ...], attempts: range) -> Comparison:
    episodes: list[EpisodeRow] = []
    kinds: list[str] = []
    pairs = None
    with path.open() as stream:
        for line in stream:
            row = Row.model_validate_json(line)
            kinds.append(row.kind)
            if row.kind == 'episode':
                episodes.append(EpisodeRow.model_validate_json(line))
            pairs = row.pairs if row.kind == 'complete' else pairs
    expected = {(case, attempt, arm) for case in cases for attempt in attempts for arm in ('baseline', 'candidate')}
    actual = {(episode.case, episode.attempt, episode.arm) for episode in episodes}
    if kinds != ['manifest', *(['episode'] * len(expected)), 'complete'] or actual != expected or pairs != len(expected) // 2:
        raise ValueError(f'incomplete or mismatched paired run: {path.name}')
    for episode in episodes:
        identity = baseline if episode.arm == 'baseline' else candidate
        if episode.candidate_sha256 != identity.digest():
            raise ValueError('episode configuration identity mismatch')
    control = metrics([episode for episode in episodes if episode.arm == 'baseline'])
    treatment = metrics([episode for episode in episodes if episode.arm == 'candidate'])
    return compare(candidate.name, control, treatment)


def run_pair(arguments: argparse.Namespace, manifest: Manifest, candidate: Candidate, partition: str) -> Comparison:
    protocol = manifest.protocol
    cases = protocol.training_cases if partition == 'training' else protocol.validation_cases
    count = protocol.training_attempts if partition == 'training' else protocol.validation_attempts
    filename = f'training-{candidate.name}.jsonl' if partition == 'training' else 'validation.jsonl'
    if snapshot() != manifest.snapshot:
        raise ValueError('source, tests, or dossier changed during campaign')
    output = arguments.out / filename
    command = [
        sys.executable,
        '-m',
        'aemon.evaluation.harness',
        'run',
        str(arguments.out / f'{candidate.name}.json'),
        '--baseline',
        str(arguments.out / f'{manifest.baseline.name}.json'),
        '--partition',
        partition,
        '--cases',
        *cases,
        '--first-attempt',
        str(protocol.first_attempt),
        '--attempts',
        str(count),
        '--url',
        arguments.url,
        '--runtime',
        arguments.runtime,
        '--out',
        str(output),
    ]
    for flag in ('expect_runtime', 'model_kind', 'model_receipt'):
        argument = vars(arguments)[flag]
        if argument is not None:
            command.extend(['--' + flag.replace('_', '-'), str(argument)])
    print(f'{partition}: {candidate.name}, {len(cases) * count} pairs starting', flush=True)
    subprocess.run(command, check=True)
    if snapshot() != manifest.snapshot:
        raise ValueError('source, tests, or dossier changed during campaign')
    comparison = read_comparison(output, candidate, manifest.baseline, cases, range(protocol.first_attempt, protocol.first_attempt + count))
    print(f'{partition}: {candidate.name}, {comparison.candidate.episodes * 2} episodes complete', flush=True)
    return comparison


def campaign(arguments: argparse.Namespace) -> Selection:
    protocol_bytes = arguments.protocol.read_bytes()
    protocol = Protocol.model_validate_json(protocol_bytes)
    baseline, candidates = configurations(protocol, arguments.protocol.parent)
    expectation = RuntimeExpectation.model_validate_json(arguments.expect_runtime.read_bytes())
    receipt = ModelReceipt.model_validate_json(arguments.model_receipt.read_bytes()) if arguments.model_receipt else None
    manifest = Manifest(
        protocol=protocol,
        protocol_sha256=hashlib.sha256(protocol_bytes).hexdigest(),
        baseline=baseline,
        candidates=candidates,
        snapshot=snapshot(),
        runtime=arguments.runtime,
        expectation=expectation,
        receipt=receipt,
        model_kind=arguments.model_kind,
    )
    arguments.out.mkdir(parents=True, exist_ok=False)
    write_json(arguments.out / 'partial.json', State(state='partial'))
    write_json(arguments.out / 'manifest.json', manifest)
    arguments.expect_runtime = arguments.out / 'runtime-expectation.json'
    write_json(arguments.expect_runtime, expectation)
    if receipt is not None:
        arguments.model_receipt = arguments.out / 'runtime-receipt.json'
        write_json(arguments.model_receipt, receipt)
    for candidate in (baseline, *candidates):
        write_json(arguments.out / f'{candidate.name}.json', candidate)
    comparisons = tuple(run_pair(arguments, manifest, candidate, 'training') for candidate in candidates)
    selection = choose(baseline.name, comparisons)
    write_json(arguments.out / 'selection.json', selection)
    validation: Literal['complete', 'skipped_no_eligible_candidate'] = 'skipped_no_eligible_candidate'
    if selection.eligible:
        winner = next(candidate for candidate in candidates if candidate.name == selection.selected)
        run_pair(arguments, manifest, winner, 'validation')
        validation = 'complete'
    write_json(arguments.out / 'complete.json', State(state='complete', selected=selection.selected, validation=validation))
    print(f'Selected {selection.selected}: {selection.reason}; independent quality review pending', flush=True)
    return selection


def parser() -> argparse.ArgumentParser:
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--protocol', type=Path, required=True)
    arguments.add_argument('--url', required=True)
    arguments.add_argument('--out', type=Path, required=True)
    arguments.add_argument('--runtime', required=True)
    arguments.add_argument('--expect-runtime', type=Path, required=True)
    arguments.add_argument('--model-kind', choices=('base', 'merged'), default='merged')
    arguments.add_argument('--model-receipt', type=Path)
    return arguments


def main() -> None:
    campaign(parser().parse_args())


if __name__ == '__main__':
    main()
