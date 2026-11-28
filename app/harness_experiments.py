"""Read-only artifact API. Include ``router`` in the app; its middleware supplies auth.

GET /api/harness/experiments returns experiments with id, state, baseline,
candidate, protocol, selection, manifest, issues, metrics and pairs. Metrics map
baseline/candidate to observed counts or null. Pairs contain case, attempt and
nullable baseline/candidate episode rows, including their full records.
Each experiment folder under experiments/harness holds protocol.json and its
configurations; the campaign's output, copied from the cluster, is in its results/
folder (selection.json and one JSONL per paired run). Completion requires one episode
per arm, case and attempt. Independent strategic quality is not evaluated here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError

from aemon.evaluation.harness.candidate import Candidate

ROOT = Path(__file__).resolve().parents[1] / 'experiments' / 'harness'
router = APIRouter(prefix='/api/harness', tags=['harness'])
Arm = Literal['baseline', 'candidate']
State = Literal['pending', 'incomplete', 'complete', 'invalid']


class Manifest(BaseModel):
    model_config = ConfigDict(extra='allow', strict=True)
    kind: Literal['manifest']
    version: Literal[2]
    candidate: Candidate
    candidate_sha256: str
    baseline: Candidate
    baseline_sha256: str
    cases: list[str] = Field(min_length=1)
    settings: dict[str, JsonValue]


class Episode(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    kind: Literal['episode']
    case: str
    attempt: int = Field(ge=0)
    arm: Arm
    candidate_sha256: str
    finished: bool
    guards_cleared: bool
    stop_reason: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    record: dict[str, Any]


class Complete(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    kind: Literal['complete']
    pairs: int = Field(ge=0)


class Metrics(BaseModel):
    episodes: int
    finished: int
    guards_cleared: int
    prompt_tokens: int
    completion_tokens: int


class Pair(BaseModel):
    case: str
    attempt: int
    baseline: Episode | None = None
    candidate: Episode | None = None


class Arms(BaseModel):
    baseline: Metrics | None = None
    candidate: Metrics | None = None


class Experiment(BaseModel):
    id: str
    state: State = 'pending'
    baseline: dict[str, JsonValue] | None = None
    candidate: dict[str, JsonValue] | None = None
    protocol: dict[str, JsonValue] | None = None
    selection: dict[str, JsonValue] | None = None
    manifest: dict[str, Any] | None = None
    issues: list[str] = Field(default_factory=list)
    metrics: Arms = Field(default_factory=Arms)
    pairs: list[Pair] = Field(default_factory=list)


class Experiments(BaseModel):
    experiments: list[Experiment]


def read_metadata(path: Path, issues: list[str]) -> dict[str, JsonValue] | None:
    if not path.exists():
        return None
    try:
        with path.open() as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict):
            raise ValueError('expected an object')
        return payload
    except (OSError, ValueError):
        issues.append(f'Cannot read {path.name} as a JSON object.')
        return None


def summarize(episodes: list[Episode], arm: Arm) -> Metrics | None:
    observed = [episode for episode in episodes if episode.arm == arm]
    if not observed:
        return None
    return Metrics(
        episodes=len(observed),
        finished=sum(episode.finished for episode in observed),
        guards_cleared=sum(episode.guards_cleared for episode in observed),
        prompt_tokens=sum(episode.prompt_tokens for episode in observed),
        completion_tokens=sum(episode.completion_tokens for episode in observed),
    )


def attempts(manifest: Manifest) -> range:
    first = manifest.settings.get('first_attempt')
    count = manifest.settings.get('attempts')
    if not isinstance(first, int) or not isinstance(count, int):
        raise ValueError('manifest settings lack first_attempt and attempts')
    return range(first, first + count)


def add_episode(row: str, manifest: Manifest, pairs: dict[tuple[str, int], Pair]) -> Episode:
    episode = Episode.model_validate_json(row)
    if episode.case not in manifest.cases or episode.attempt not in attempts(manifest):
        raise ValueError('episode outside requested cases or attempts')
    expected_digest = manifest.baseline_sha256 if episode.arm == 'baseline' else manifest.candidate_sha256
    if episode.candidate_sha256 != expected_digest:
        raise ValueError('episode candidate mismatch')
    record = episode.record
    if record.get('case') != episode.case or not isinstance(record.get('calls'), list):
        raise ValueError('invalid trace record')
    if bool(record.get('final')) != episode.finished or episode.guards_cleared and not episode.finished:
        raise ValueError('inconsistent episode outcome')
    key = (episode.case, episode.attempt)
    pair = pairs.setdefault(key, Pair(case=episode.case, attempt=episode.attempt))
    if episode.arm == 'baseline':
        if pair.baseline is not None:
            raise ValueError('duplicate baseline')
        pair.baseline = episode
    else:
        if pair.candidate is not None:
            raise ValueError('duplicate candidate')
        pair.candidate = episode
    return episode


def read_rows(lines: list[str], experiment: Experiment) -> None:
    manifest = Manifest.model_validate_json(lines[0])
    identities = manifest.candidate.digest() == manifest.candidate_sha256 and manifest.baseline.digest() == manifest.baseline_sha256
    if len(set(manifest.cases)) != len(manifest.cases) or not identities:
        raise ValueError('manifest identity mismatch')
    experiment.manifest = manifest.model_dump(mode='json')
    experiment.candidate = manifest.candidate.model_dump(mode='json')
    pairs: dict[tuple[str, int], Pair] = {}
    episodes: list[Episode] = []
    complete = False
    for index, line in enumerate(lines[1:], start=1):
        if complete:
            raise ValueError('rows after completion')
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise
            experiment.issues.append('Last row is truncated; only preceding rows are shown.')
            break
        if isinstance(payload, dict) and payload.get('kind') == 'complete':
            marker = Complete.model_validate_json(line)
            complete = marker.pairs == len(manifest.cases) * len(attempts(manifest)) == len(pairs)
            if not complete or any(pair.baseline is None or pair.candidate is None for pair in pairs.values()):
                raise ValueError('completion does not match expected pairs')
        else:
            episodes.append(add_episode(line, manifest, pairs))
    experiment.pairs = list(pairs.values())
    experiment.metrics = Arms(baseline=summarize(episodes, 'baseline'), candidate=summarize(episodes, 'candidate'))
    experiment.state = 'complete' if complete else 'incomplete'


def read_campaign(path: Path, root: Path) -> Experiment:
    experiment = Experiment(id=path.relative_to(root).as_posix())
    try:
        with path.open() as stream:
            lines = [line for line in stream if line.strip()]
        if not lines:
            experiment.state = 'incomplete'
            experiment.issues.append('Campaign file is empty; no results recorded.')
        else:
            read_rows(lines, experiment)
    except (OSError, UnicodeError, ValueError, ValidationError):
        experiment.state = 'invalid'
        experiment.metrics = Arms()
        experiment.pairs = []
        experiment.issues.append('Invalid campaign: check row schema, candidate identity, duplicates and completion count.')
    return experiment


def configured_candidates(directory: Path, protocol: dict[str, JsonValue] | None) -> list[Path]:
    names = protocol.get('candidates') if protocol else None
    if not isinstance(names, list):
        return []
    return [directory / name for name in names if isinstance(name, str)]


def read_experiment(directory: Path, root: Path) -> list[Experiment]:
    issues: list[str] = []
    protocol = read_metadata(directory / 'protocol.json', issues)
    baseline_name = protocol.get('baseline') if protocol else None
    baseline = read_metadata(directory / baseline_name, issues) if isinstance(baseline_name, str) else None
    results = directory / 'results'
    selection = read_metadata(results / 'selection.json', issues)
    experiments = [read_campaign(path, root) for path in sorted(results.glob('*.jsonl')) if not path.is_symlink()]
    observed = {str(experiment.candidate.get('name')) for experiment in experiments if experiment.candidate}
    for path in configured_candidates(directory, protocol):
        pending = Experiment(id=path.relative_to(root).as_posix())
        pending.candidate = read_metadata(path, pending.issues)
        if pending.candidate is None or pending.candidate.get('name') not in observed:
            if pending.issues:
                pending.state = 'invalid'
            experiments.append(pending)
    for experiment in experiments:
        experiment.baseline = baseline
        experiment.protocol = protocol
        experiment.selection = selection
        experiment.issues.extend(issues)
    return experiments


def list_experiments(root: Path) -> Experiments:
    experiments = [
        experiment for directory in sorted(root.glob('*/')) if (directory / 'protocol.json').exists() for experiment in read_experiment(directory, root)
    ]
    if not experiments:
        experiments.append(Experiment(id='pending', issues=['No campaign results have been recorded.']))
    return Experiments(experiments=experiments)


@router.get('/experiments', response_model=Experiments)
def experiments() -> Experiments:
    return list_experiments(ROOT)
