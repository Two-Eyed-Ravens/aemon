"""The harness page's API reads what the campaign actually writes."""

import json
from dataclasses import asdict
from pathlib import Path

import harness_experiments
from aemon.common.types import Json, Message, Schema
from aemon.evaluation.harness.__main__ import metadata
from aemon.evaluation.harness.candidate import Candidate
from aemon.evaluation.harness.runner import paired, select_cases
from aemon.evaluation.harness.runtime import RuntimeIdentity


def repeated_brief(messages: list[Message], seed: int, max_tokens: int, schema: Schema | None, temperature: float) -> Json:
    return {'text': '{"name":"read_brief","arguments":{}}', 'prompt_tokens': 10, 'completion_tokens': 2}


def test_api_reads_a_paired_run_written_by_the_runner(tmp_path: Path) -> None:
    experiment = tmp_path / 'recovery_v1'
    (experiment / 'results').mkdir(parents=True)
    baseline = Candidate(name='baseline', features=('budget',))
    candidate = Candidate(name='rereads', features=('budget', 'mask_rereads'))
    (experiment / 'baseline.json').write_text(baseline.model_dump_json())
    (experiment / 'rereads.json').write_text(candidate.model_dump_json())
    (experiment / 'protocol.json').write_text(json.dumps({'baseline': 'baseline.json', 'candidates': ['rereads.json']}))
    case_id = 'trumpf-new-evidence-irrelevant'
    case = select_cases([case_id], 'training')[0]
    manifest = metadata(candidate, baseline, 'test', [case_id], 'training', 7, 2, RuntimeIdentity({}, 0))
    rows = [manifest]
    for attempt in (7, 8):
        rows += [{'kind': 'episode', **asdict(episode)} for episode in paired(case, attempt, candidate, repeated_brief, baseline)]
    rows.append({'kind': 'complete', 'pairs': 2})
    (experiment / 'results' / 'training-rereads.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))

    listed = harness_experiments.list_experiments(tmp_path).experiments

    assert [(item.state, item.issues) for item in listed] == [('complete', [])]
    assert listed[0].metrics.baseline is not None
    assert listed[0].metrics.baseline.episodes == 2
