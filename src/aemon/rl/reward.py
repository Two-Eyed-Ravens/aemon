"""A step reward checked by the tools (DECISIONS, 20 November, registered and amended): replay an investigation state,
execute a candidate next call in the guarded tools, and score it. No LLM judge is involved.

-1   not a parseable tool call, a repeat of an earlier call, or a refusal for a grounding error (a quote not in its
     source, a fabricated source, a simulated result cited as evidence, a repeat the tools themselves refuse)
-0.5 any other refusal (wrong stage, bad arguments, order, budget)
+0.5 accepted
+1   accepted and progressing: the accepted state changes (brief, frame, reads, theories, assessments, challenges,
     tests, declines, revisions, finish) or the stage moves on

It rewards working, non-repeating, grounded calls. It cannot see whether a call is wise: a process check, not a
judgement of quality.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from aemon.agent.backends.llama_client import parse_call
from aemon.agent.recovery import signature
from aemon.environment.stages import current_stage
from aemon.environment.tools import Investigation

if TYPE_CHECKING:
    from aemon.common.types import Json
    from aemon.environment.tools import Case

GROUNDING_ERRORS = frozenset({'misquote', 'fabricated', 'synthetic_as_evidence', 'repeat'})


@dataclass(frozen=True)
class StepReward:
    value: float
    reason: str


def fresh_run(settings: Json, case: Case) -> Investigation:
    return Investigation(
        case,
        settings.get('complete_workflow', False),
        True,
        settings.get('quote_marks', False),
        settings.get('reread_limit'),
        settings.get('source_dates', False),
        settings.get('min_assessed', 1),
        status_check=settings.get('status_check', False),
    )


def call_key(name: object, arguments: object) -> tuple[str, str]:
    return str(name), json.dumps(arguments, sort_keys=True)


def score_call(run: Investigation, name: object, arguments: object) -> StepReward:
    """Execute one call on run (which it changes) and score it."""
    if call_key(name, arguments) in {call_key(c['name'], c['arguments']) for c in run.calls}:
        run.call(name, arguments)
        return StepReward(-1.0, 'repeats an earlier call')
    before, stage = signature(run), current_stage(run).name
    result = run.call(name, arguments)
    if 'error' in result:
        category = run.calls[-1].get('category', '')
        if category in GROUNDING_ERRORS:
            return StepReward(-1.0, f'refused: {category}')
        return StepReward(-0.5, f'refused: {category}')
    if signature(run) != before or current_stage(run).name != stage:
        return StepReward(1.0, 'accepted, progress')
    return StepReward(0.5, 'accepted')


def replay_to(record: Json, case: Case, upto: int) -> Investigation:
    """The investigation after the first upto recorded model turns."""
    run = fresh_run(record['settings'], case)
    for turn in record['model_turns'][:upto]:
        call, _ = parse_call(turn['text'], True)
        if call is not None:
            run.call(call['name'], call['arguments'])
    return run


def step_reward(record: Json, case: Case, upto: int, reply_text: str) -> StepReward:
    """The reward of reply_text as the next turn after the first upto recorded turns of record."""
    call, _ = parse_call(reply_text, True)
    if call is None:
        return StepReward(-1.0, 'not a parseable tool call')
    return score_call(replay_to(record, case, upto), call['name'], call['arguments'])


def run_rewards(record: Json, case: Case) -> list[StepReward]:
    """The reward of every recorded turn of a run, in one replay."""
    run = fresh_run(record['settings'], case)
    rewards = []
    for turn in record['model_turns']:
        call, _ = parse_call(turn['text'], True)
        if call is None:
            rewards.append(StepReward(-1.0, 'not a parseable tool call'))
            continue
        rewards.append(score_call(run, call['name'], call['arguments']))
    return rewards
