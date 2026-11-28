"""Validate candidates or run sequential pairs with checked runtime identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict
from pathlib import Path

from pydantic import TypeAdapter

from aemon.agent.backends.llama_client import chat
from aemon.common.paths import ROOT
from aemon.common.types import Json, Message, Schema
from aemon.evaluation.harness.candidate import Candidate, load_candidate
from aemon.evaluation.harness.runner import paired, select_cases
from aemon.evaluation.harness.runtime import Adapter, ModelReceipt, ModelSelection, RuntimeExpectation, RuntimeIdentity, inspect_runtime


def parser() -> argparse.ArgumentParser:
    arguments = argparse.ArgumentParser(description=__doc__)
    commands = arguments.add_subparsers(dest='command', required=True)
    validate = commands.add_parser('validate')
    validate.add_argument('candidate', type=Path)
    run = commands.add_parser('run')
    run.add_argument('candidate', type=Path)
    run.add_argument('--baseline', type=Path)
    run.add_argument('--cases', nargs='+', required=True)
    run.add_argument('--partition', choices=('training', 'validation'), required=True)
    run.add_argument('--url', required=True)
    run.add_argument('--runtime', default='', help='operator label, not an attestation')
    run.add_argument('--expect-runtime', type=Path, required=True)
    run.add_argument('--model-receipt', type=Path)
    run.add_argument('--model-kind', choices=('base', 'merged', 'adapter'), default='base')
    run.add_argument('--adapter-map', type=Path, help='JSON list of every loaded adapter id/path/scale')
    run.add_argument('--first-attempt', type=int, default=0)
    run.add_argument('--attempts', type=int, default=1)
    run.add_argument('--out', type=Path, required=True)
    return arguments


def tree_digest(root: Path, pattern: str) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob(pattern)):
        digest.update(path.relative_to(root).as_posix().encode() + b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def revision() -> str:
    supplied = os.environ.get('CODE_REVISION', '').strip()
    if supplied:
        return supplied
    return subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()


def metadata(
    candidate: Candidate, baseline: Candidate, runtime: str, cases: list[str], partition: str, first_attempt: int, attempts: int, identity: RuntimeIdentity
) -> Json:
    return {
        'kind': 'manifest',
        'version': 2,
        'revision': revision(),
        'source_sha256': tree_digest(ROOT / 'src', '*.py'),
        'tests_sha256': tree_digest(ROOT / 'tests', '*.py'),
        'data_sha256': tree_digest(ROOT / 'data' / 'dossier', '*.json'),
        'candidate': candidate.model_dump(mode='json'),
        'candidate_sha256': candidate.digest(),
        'baseline': baseline.model_dump(mode='json'),
        'baseline_sha256': baseline.digest(),
        'runtime': runtime,
        'runtime_identity': identity.evidence,
        'cases': cases,
        'partition': partition,
        'settings': {
            'max_turns': 45,
            'max_errors': 4,
            'max_tokens': 520,
            'prompt': 'compact',
            'first_attempt': first_attempt,
            'attempts': attempts,
            'temperature': 0,
            'error_temperature': 0.4,
            'redraw_temperature': 0.8,
            'max_redraws': 3,
            'lora': identity.lora,
            'seed_rule': 'sum(ord(c) for c in case_id) + 1000 * attempt',
        },
    }


def runtime_from_arguments(arguments: argparse.Namespace) -> RuntimeIdentity:
    expected = RuntimeExpectation.model_validate_json(arguments.expect_runtime.read_text())
    receipt = ModelReceipt.model_validate_json(arguments.model_receipt.read_text()) if arguments.model_receipt else None
    adapters = ()
    if arguments.adapter_map:
        adapters = TypeAdapter(tuple[Adapter, ...]).validate_json(arguments.adapter_map.read_text())
    selection = ModelSelection(kind=arguments.model_kind, adapters=adapters)
    return inspect_runtime(arguments.url, expected, selection, receipt)


def run(arguments: argparse.Namespace, candidate: Candidate) -> None:
    if arguments.attempts < 1 or arguments.first_attempt < 0:
        raise ValueError('attempts must be positive and first-attempt nonnegative')
    baseline = load_candidate(arguments.baseline) if arguments.baseline else Candidate(name='baseline')
    cases = select_cases(arguments.cases, arguments.partition)
    with arguments.out.open('x') as stream:
        identity = runtime_from_arguments(arguments)
        manifest = metadata(candidate, baseline, arguments.runtime, arguments.cases, arguments.partition, arguments.first_attempt, arguments.attempts, identity)
        stream.write(json.dumps(manifest) + '\n')
        stream.flush()

        def respond(messages: list[Message], seed: int, max_tokens: int, schema: Schema | None, temperature: float) -> Json:
            return chat(arguments.url, messages, seed, max_tokens, schema, temperature, lora=identity.lora)

        for case in cases:
            for attempt in range(arguments.first_attempt, arguments.first_attempt + arguments.attempts):
                for episode in paired(case, attempt, candidate, respond, baseline):
                    stream.write(json.dumps({'kind': 'episode', **asdict(episode)}) + '\n')
                    stream.flush()
        stream.write(json.dumps({'kind': 'complete', 'pairs': len(cases) * arguments.attempts}) + '\n')


def main() -> None:
    arguments = parser().parse_args()
    candidate = load_candidate(arguments.candidate)
    if arguments.command == 'validate':
        print(json.dumps({'candidate': candidate.model_dump(), 'sha256': candidate.digest()}))
        return
    run(arguments, candidate)


if __name__ == '__main__':
    main()
