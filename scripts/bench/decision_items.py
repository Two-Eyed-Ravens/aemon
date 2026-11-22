"""Items for the first decision-model measurement (product plan, workstream A): two typed sub-decisions with gold labels
already in the repository, built from the saved runs of both frozen tests.

1. Evidence kind of a quoted passage. Gold: the dossier's annotation (`data/dossier/evidence.json`, v1; only records
   whose kind is one of the tool's six). The agent's own choices come from every accepted `assess_evidence` in the
   version 1 and final-system runs. One item per (record, quote).
2. Propose or decline a test. Gold: the case's `test_warranted`. The agent's choice: a proposed test, a declined
   test, or neither (the run never reached the test stage). One item per case.

Usage: python scripts/bench/decision_items.py --out DIR  -> DIR/decision_items.jsonl
"""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KINDS = ['regulation', 'independent_study', 'customer_observation', 'company_assertion', 'analogy', 'market_fact']
RUNS = {
    'final': {'version 1': 'reports/judge/final/final_test_trained_adapter.json', 'final system': 'experiments/grounded/final/D.json'},
    'test2': {'version 1': 'reports/judge/test2/test2_trained_adapter.json', 'final system': 'experiments/grounded/test2/D.json'},
}
CASES = {'final': 'data/dossier/cases_heldout.json', 'test2': 'data/dossier/cases_heldout2.json'}


def load_cases(path: str) -> dict[str, dict]:
    c = json.load(open(ROOT / path))
    cs = c if isinstance(c, list) else c.get('cases', c)
    return {x['id']: x for x in cs} if isinstance(cs, list) else cs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    dossier = {r['id']: r for r in json.load(open(ROOT / 'data/dossier/evidence.json'))['records']}

    kind_items: dict[tuple, dict] = {}
    test_items: dict[str, dict] = {}
    for split, arms in RUNS.items():
        cases = load_cases(CASES[split])
        for arm, path in arms.items():
            for rec in json.load(open(ROOT / path))['records']:
                for x in rec['assessments']:
                    src = dossier.get(x['evidence_id'])
                    if not src or src['kind'] not in KINDS or not x.get('quote'):
                        continue
                    key = (x['evidence_id'], x['quote'])
                    it = kind_items.setdefault(key, {
                        'task': 'evidence_kind', 'split': split, 'record': x['evidence_id'], 'quote': x['quote'],
                        'title': src.get('title', ''), 'origin': src.get('type', ''), 'gold': src['kind'],
                        'agent': defaultdict(list)})
                    it['agent'][arm].append(x['evidence_kind'])
                case = cases.get(rec['case'])
                if case is None:
                    continue
                it = test_items.setdefault(rec['case'], {
                    'task': 'test_choice', 'split': split, 'case': rec['case'], 'company': rec['company'],
                    'question': case['question'], 'brief': case['brief'], 'budget': case.get('test_budget'),
                    'weeks': case.get('max_test_weeks'), 'gold': 'propose' if case['test_warranted'] else 'decline',
                    'agent': defaultdict(list)})
                choice = 'propose' if rec.get('tests') else 'decline' if rec.get('test_declined') else 'not reached'
                it['agent'][arm].append(choice)

    items = []
    for it in list(kind_items.values()) + list(test_items.values()):
        it['agent'] = dict(it['agent'])
        it['id'] = len(items)
        items.append(it)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'decision_items.jsonl'
    p.write_text(''.join(json.dumps(i, ensure_ascii=False) + '\n' for i in items))
    n_kind = sum(i['task'] == 'evidence_kind' for i in items)
    print(f'{len(items)} items ({n_kind} evidence kind, {len(items) - n_kind} test choice)',
          hashlib.sha256(p.read_bytes()).hexdigest()[:16], p)


if __name__ == '__main__':
    main()
