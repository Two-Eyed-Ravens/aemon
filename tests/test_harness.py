"""Candidate boundaries and paired execution against the real guarded environment."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from aemon.common.paths import ROOT
from aemon.common.types import Json, Message, Schema
from aemon.evaluation.harness.campaign import Protocol, configurations
from aemon.evaluation.harness.candidate import Candidate, load_candidate
from aemon.evaluation.harness.runner import paired, select_cases


def repeated_brief(messages: list[Message], seed: int, max_tokens: int, schema: Schema | None, temperature: float) -> Json:
    return {'text': '{"name":"read_brief","arguments":{}}', 'prompt_tokens': 10, 'completion_tokens': 2}


@pytest.mark.parametrize(
    'payload',
    [
        '{"name":"test","features":["decide_kind"]}',
        '{"name":"test","features":["budget","budget"]}',
        '{"name":"test","features":["evidence_first"]}',
        '{"name":"test","max_errors":100}',
    ],
)
def test_candidate_rejects_unsupported_configuration(payload: str) -> None:
    with pytest.raises(ValidationError):
        Candidate.model_validate_json(payload)


def test_candidate_identity_is_independent_of_feature_order() -> None:
    first = Candidate(name='test', features=('budget', 'progress'))
    second = Candidate(name='test', features=('progress', 'budget'))
    assert first.digest() == second.digest()


def test_candidate_is_immutable() -> None:
    candidate = Candidate(name='test')
    with pytest.raises(ValidationError):
        candidate.name = 'changed'


def test_json_candidate_loads_through_public_entry_point(tmp_path: Path) -> None:
    path = tmp_path / 'candidate.json'
    path.write_text('{"name":"budget","features":["budget"]}')
    assert load_candidate(path).features == ('budget',)


def test_training_partition_rejects_validation_company() -> None:
    with pytest.raises(ValueError, match='outside the training partition'):
        select_cases(['hellberg-new-evidence-looks'], 'training')


def test_selector_rejects_cases_outside_development() -> None:
    with pytest.raises(ValueError, match='outside development'):
        select_cases(['unknown-frozen-case'], 'training')


def test_paired_execution_keeps_baseline_separate_and_counts_usage() -> None:
    case = select_cases(['hellberg-new-evidence-looks'], 'validation')[0]
    candidate = Candidate(name='budget', features=('budget',))
    baseline, treatment = paired(case, 0, candidate, repeated_brief)
    assert 'recovery' not in baseline.record['settings']
    assert treatment.record['settings']['recovery'] == ['budget']
    assert baseline.stop_reason == treatment.stop_reason == 'repeated errors'
    assert baseline.prompt_tokens == treatment.prompt_tokens == 50
    assert baseline.completion_tokens == treatment.completion_tokens == 10
    assert not baseline.guards_cleared
    assert not treatment.guards_cleared


def test_validate_cli_reports_candidate_identity(tmp_path: Path) -> None:
    path = tmp_path / 'candidate.json'
    path.write_text('{"name":"budget","features":["budget"]}')
    completed = subprocess.run(
        [sys.executable, '-m', 'aemon.evaluation.harness', 'validate', str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    receipt = json.loads(completed.stdout)
    assert receipt['sha256'] == load_candidate(path).digest()


def test_run_cli_refuses_existing_output_before_inference(tmp_path: Path) -> None:
    candidate = tmp_path / 'candidate.json'
    candidate.write_text('{"name":"budget","features":["budget"]}')
    output = tmp_path / 'paired.jsonl'
    output.write_text('existing evidence\n')
    completed = subprocess.run(
        [
            sys.executable,
            '-m',
            'aemon.evaluation.harness',
            'run',
            str(candidate),
            '--partition',
            'validation',
            '--cases',
            'hellberg-new-evidence-looks',
            '--url',
            'http://127.0.0.1:1',
            '--runtime',
            'test',
            '--expect-runtime',
            str(tmp_path / 'runtime.json'),
            '--out',
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert 'FileExistsError' in completed.stderr
    assert output.read_text() == 'existing evidence\n'


def test_registered_recovery_protocol_loads_with_the_evaluated_guards() -> None:
    directory = ROOT / 'experiments' / 'harness' / 'recovery_v1'
    protocol = Protocol.model_validate_json((directory / 'protocol.json').read_text())
    baseline, candidates = configurations(protocol, directory)
    assert set(baseline.features) == {'no_repeats', 'quote_menu', 'resample_repeats', 'budget', 'grounded_beliefs', 'evidence_first'}
    assert len(candidates) == 3
