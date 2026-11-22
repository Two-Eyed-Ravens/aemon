"""Recovery rows from teacher episodes, built by rule: no model writes anything here. NOTHING HERE TRAINS.

The fine-tuned Qwen students of 19 November repeat calls and keep citing a simulated result in finish (DECISIONS,
19 November 10:40 and 12:10), while no teacher row shows either mistake or what follows it. So each teacher episode
already in the training rows is replayed through the tools, and at chosen turns a copy of the investigation receives
that mistake first:
- repeat: the teacher's previous accepted call again, which the tools must refuse;
- simulated_finish: at the teacher's finish, a finish that also cites a simulated source the run has read, which the
  tools must refuse as synthetic_as_evidence.
The row's context is the compact state after that refusal, exactly as the student would see it, and its target is the
teacher's own next reply, which must then be accepted on the copy. Rows are tagged source: recovery-rule.

Usage: python -m aemon.rows.recovery_rows --reports A.json ... --training-rows final.jsonl --manifest M.jsonl \
           --per-episode 2 --output recovery.jsonl
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from aemon.agent.backends.llama_client import parse_call
from aemon.agent.state_view import guidance, next_step, state_of
from aemon.common.constants.env import SYNTHETIC_CLASSES
from aemon.common.constants.prompts import PROMPTS
from aemon.common.types import Json
from aemon.data.splits import is_validation
from aemon.environment.cases import load_cases
from aemon.environment.stages import current_stage
from aemon.environment.tools import Case, Investigation
from aemon.evaluation.diagnostics.audit import ReplayMismatch
from aemon.rows.provenance import training_source

SOURCE = 'recovery-rule'


@dataclass
class TeacherTurn:
    """The investigation just before a teacher reply, and that reply."""

    run: Investigation
    text: str
    call: Json


def teacher_turns(record: Json, case: Case) -> Iterator[TeacherTurn]:
    """Replays the record as build_rows.transcript does, yielding each accepted teacher call with the state before it."""
    settings = record.get('settings', {})
    run = Investigation(
        case,
        settings.get('complete_workflow', False),
        settings.get('staged', False),
        settings.get('quote_marks', False),
        settings.get('reread_limit'),
        settings.get('source_dates', False),
        settings.get('min_assessed', 1),
        status_check=settings.get('status_check', False),
    )
    for index, turn in enumerate(record['model_turns']):
        call, problem = parse_call(turn['text'], True)
        before = copy.deepcopy(run)
        result = run.call(call['name'], call['arguments']) if call is not None else {'error': problem}
        if json.dumps(result, sort_keys=True) != json.dumps(turn['tool_result'], sort_keys=True):
            raise ReplayMismatch(f'turn {index + 1} returned something else on replay')
        if call is not None and 'error' not in result:
            yield TeacherTurn(before, turn['text'], call)
        if run.final is not None:
            return


def shown_after(run: Investigation, result: Json) -> Json:
    """The tool result with the guidance the runner adds to it, as build_rows shows it."""
    return {**result, **guidance(run)} if run.staged else dict(result, next=next_step(run))


def recovery_row(turn: TeacherTurn, mistake: Json, system: str) -> Json | None:
    """The row teaching the teacher's reply after the mistake, or None if the tools accept the mistake or then refuse
    the reply."""
    trial = copy.deepcopy(turn.run)
    refused = trial.call(mistake['name'], mistake['arguments'])
    if 'error' not in refused:
        return None
    context = state_of(trial, shown_after(trial, refused))
    stage = current_stage(trial).name if trial.staged else None
    check = copy.deepcopy(trial)
    if 'error' in check.call(turn.call['name'], turn.call['arguments']):
        return None
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': context}, {'role': 'assistant', 'content': turn.text}]
    return {'messages': messages, 'target_index': 2, 'stage': stage, 'mistake': refused['error']}


def simulated_finish(turn: TeacherTurn) -> Json | None:
    """The teacher's finish with a simulated source it has read added to the evidence, if there is one."""
    if turn.call['name'] != 'finish':
        return None
    simulated = sorted(i for i in turn.run.read if turn.run._source(i).type in SYNTHETIC_CLASSES)
    if not simulated:
        return None
    arguments = dict(turn.call['arguments'], evidence_ids=[*turn.call['arguments']['evidence_ids'], simulated[0]])
    return {'name': 'finish', 'arguments': arguments}


def previous_call(turn: TeacherTurn) -> Json | None:
    accepted = [c for c in turn.run.calls if c.get('accepted')]
    if not accepted:
        return None
    return {'name': accepted[-1]['name'], 'arguments': accepted[-1]['arguments']}


def episode_rows(record: Json, case: Case, system: str, per_episode: int, episode: str) -> list[Json]:
    """Every simulated-finish row, and up to per_episode repeat rows at turns drawn with a seed from the episode id."""
    turns = list(teacher_turns(record, case))
    rows = []
    for turn in turns:
        mistake = simulated_finish(turn)
        row = recovery_row(turn, mistake, system) if mistake else None
        if row:
            rows.append(dict(row, kind='simulated_finish'))
    rng = random.Random(int(hashlib.sha256(episode.encode()).hexdigest()[:8], 16))
    repeats = 0
    for turn in rng.sample(turns[1:], len(turns) - 1):
        mistake = previous_call(turn)
        row = recovery_row(turn, mistake, system) if mistake else None
        if row and repeats < per_episode:
            rows.append(dict(row, kind='repeat'))
            repeats += 1
    return rows


def build(reports: list[str], training_episodes: set[str], manifest: str, prompt: str, per_episode: int) -> tuple[list[Json], Counter[str]]:
    cases = {c.id: c for c in load_cases()}
    rows: list[Json] = []
    counts: Counter[str] = Counter()
    for path in reports:
        report = json.loads(Path(path).read_text())
        protocol = (report.get('protocol') or {}).get('id')
        for record in report['records']:
            if is_validation(record['case']) or record['case'] not in cases:
                counts['validation or unknown case'] += 1
                continue
            try:
                source = training_source(record['model_turns'], cases[record['case']], protocol, manifest)
            except ValueError:
                counts['not a permitted teacher episode'] += 1
                continue
            if source.episode not in training_episodes:
                counts['not in the training rows'] += 1
                continue
            made = episode_rows(record, cases[record['case']], PROMPTS[prompt], per_episode, source.episode)
            counts['episodes used'] += 1
            for row in made:
                counts[row['kind']] += 1
                rows.append(dict(row, case=record['case'], episode=source.episode, teacher_weights=source.weights_sha256, source=SOURCE))
    return rows, counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--reports', nargs='+', required=True)
    parser.add_argument('--training-rows', required=True, help='the rows these episodes are already in; others are skipped')
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--prompt', default='compact')
    parser.add_argument('--per-episode', type=int, default=2, help='repeat rows per episode')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error('rows are never overwritten')
    with open(args.training_rows) as handle:
        episodes = {json.loads(line)['episode'] for line in handle}
    rows, counts = build(args.reports, episodes, args.manifest, args.prompt, args.per_episode)
    output.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    print(json.dumps({'rows': len(rows), **counts}, indent=1))


if __name__ == '__main__':
    main()
