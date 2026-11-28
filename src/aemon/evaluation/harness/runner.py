"""Trusted paired execution with fixed budgets and independently computed checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from aemon.agent.loop import play
from aemon.agent.records import record_of
from aemon.agent.tool_schemas import TOOL_SCHEMA
from aemon.common.constants.prompts import PROMPTS
from aemon.common.types import Json, Respond
from aemon.data.splits import is_validation
from aemon.environment.cases import load_cases
from aemon.environment.checks import guards_cleared, run_checks
from aemon.environment.tools import Case
from aemon.evaluation.harness.candidate import Candidate

Partition = Literal['training', 'validation']


@dataclass(frozen=True)
class Episode:
    case: str
    attempt: int
    arm: str
    candidate_sha256: str
    finished: bool
    guards_cleared: bool
    stop_reason: str
    prompt_tokens: int
    completion_tokens: int
    record: Json


def select_cases(case_ids: list[str], partition: Partition) -> list[Case]:
    """Resolve only development cases and enforce company-level separation."""
    if not case_ids or len(set(case_ids)) != len(case_ids):
        raise ValueError('provide distinct development case ids')
    available = {case.id: case for case in load_cases()}
    selected = []
    for case_id in case_ids:
        if case_id not in available:
            raise ValueError(f'case is outside development: {case_id}')
        if is_validation(case_id) != (partition == 'validation'):
            raise ValueError(f'case is outside the {partition} partition: {case_id}')
        selected.append(available[case_id])
    return selected


def evaluate(case: Case, attempt: int, candidate: Candidate, respond: Respond, arm: str) -> Episode:
    run, info = play(
        case,
        respond,
        PROMPTS['compact'],
        45,
        4,
        520,
        True,
        TOOL_SCHEMA,
        staged=True,
        compact=True,
        quote_marks=True,
        attempt=attempt,
        recovery_features=candidate.features,
    )
    checks = run_checks(run)
    finished = run.final is not None
    cleared = finished and guards_cleared(checks)
    record = record_of(run, info)
    record['checks'] = checks
    return Episode(
        case.id,
        attempt,
        arm,
        candidate.digest(),
        finished,
        cleared,
        info['stop_reason'],
        sum(turn.get('aggregate_usage', turn).get('prompt_tokens', 0) for turn in info['turns']),
        sum(turn.get('aggregate_usage', turn).get('completion_tokens', 0) for turn in info['turns']),
        record,
    )


def paired(case: Case, attempt: int, candidate: Candidate, respond: Respond, baseline: Candidate | None = None) -> tuple[Episode, Episode]:
    baseline = baseline if baseline is not None else Candidate(name='baseline')
    control = evaluate(case, attempt, baseline, respond, 'baseline')
    treatment = evaluate(case, attempt, candidate, respond, 'candidate')
    return control, treatment
