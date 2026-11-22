"""Run AuditKIT retrospectively on saved run reports whose run skipped it (the runner's environment lacked AgentTune).

AuditKIT replays each recorded investigation's tool calls through the guarded tools (no model response is regenerated)
and scores them. The original report is left untouched: the audit goes to a separate file beside it,
`<report>.auditkit.json`, with the input report's sha256, the AgentTune and AuditKIT versions, the code revision and a
note that it was performed retrospectively. Reports whose run already carries an AuditKIT section are skipped.

Usage: python scripts/bench/audit_reports.py --split development REPORT.json [REPORT.json ...]
"""

import argparse
import hashlib
import json
import os
from importlib.metadata import version
from pathlib import Path

from aemon.environment.cases import load_cases
from aemon.evaluation.diagnostics.audit import audit


def audit_report(path: Path, split: str) -> str:
    raw = path.read_bytes()
    report = json.loads(raw)
    existing = report.get('auditkit')
    if existing and 'skipped' not in existing:
        return 'audited during the run, left as is'
    section = audit(report['records'], load_cases('all', split=split))
    sidecar = {
        'performed': 'retrospectively, on the saved trajectories (replay of the recorded tool calls; no model calls)',
        'report': path.name,
        'report_sha256': hashlib.sha256(raw).hexdigest(),
        'run_skipped_because': existing.get('skipped') if existing else 'absent',
        'agenttune_version': version('agenttune'),
        'auditkit_version': version('auditkit'),
        'code_revision': os.environ.get('CODE_REVISION', 'unknown'),
        'auditkit': section,
    }
    out = path.with_name(path.stem + '.auditkit.json')
    out.write_text(json.dumps(sidecar, indent=1))
    return f'audited retrospectively: replay mismatches {section["replay_mismatches"]} -> {out.name}'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--split', default='development')
    parser.add_argument('reports', nargs='+', type=Path)
    args = parser.parse_args()
    for path in args.reports:
        print(path.name, audit_report(path, args.split), flush=True)


if __name__ == '__main__':
    main()
