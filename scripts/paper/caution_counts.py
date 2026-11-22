"""Over-caution counts beside the quality gain (main table): runs that do not finish, declined tests on cases whose
test_warranted label says a test was warranted (labels contestable), and finishes whose recommendation begins
"Insufficient evidence". Harness counts from the saved run reports, development split.

Usage: uv run python scripts/paper/caution_counts.py NAME=REPORT.json [NAME=REPORT.json ...]
"""

import argparse
import json
from pathlib import Path

from aemon.environment.cases import load_cases

ABSTAIN_PREFIX = 'insufficient evidence'


def counts(path: Path, warranted: dict[str, bool]) -> dict:
    records = json.loads(path.read_text())['records']
    declined = [r for r in records if r['test_declined'] and not r['tests']]
    finished = [r for r in records if r['stop_reason'] == 'finished']
    abstained = [r for r in finished if str((r['final'] or {}).get('recommendation', '')).strip().lower().startswith(ABSTAIN_PREFIX)]
    return {
        'runs': len(records),
        'not_finished': len(records) - len(finished),
        'declined': len(declined),
        'declined_where_test_warranted': sum(warranted[r['case']] for r in declined),
        'insufficient_evidence_finishes': len(abstained),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('arms', nargs='+')
    args = parser.parse_args()
    warranted = {case.id: case.test_warranted for case in load_cases()}
    result = {}
    for spec in args.arms:
        name, _, path = spec.partition('=')
        result[name] = counts(Path(path), warranted)
        print(name, json.dumps(result[name]))


if __name__ == '__main__':
    main()
