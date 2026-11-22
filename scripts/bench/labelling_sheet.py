"""Sheets for the human benchmark (product plan, gate 2): blind analyst labels on the saved runs of both frozen tests,
so the typed sub-decisions, the judges and later models can be scored against people for the first time.

Three CSV sheets, each row self-contained and with nothing that names the model or the arm:
  assessments.csv     one quoted passage and the theory it was weighed for: label the evidence kind and the direction;
  tests.csv           one case: should a test be proposed or declined, and why;
  recommendations.csv one finished investigation's position and recommendation: score it 0-3 and list unsupported claims.
A key file (key.json, kept apart from the sheets) maps each row back to its run, arm and the agent's own choice.

Rows are sampled with a fixed seed, evenly over companies, from version 1 and the final system.

Usage: python scripts/bench/labelling_sheet.py --out DIR [--assessments 300] [--recommendations 60]
"""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = 11
RUNS = {
    ('final', 'version 1'): 'reports/judge/final/final_test_trained_adapter.json',
    ('final', 'final system'): 'experiments/grounded/final/D.json',
    ('test2', 'version 1'): 'reports/judge/test2/test2_trained_adapter.json',
    ('test2', 'final system'): 'experiments/grounded/test2/D.json',
}
CASES = {'final': 'data/dossier/cases_heldout.json', 'test2': 'data/dossier/cases_heldout2.json'}


def even_sample(rows: list[dict], key: str, n: int, rng: random.Random) -> list[dict]:
    """Up to n rows, round-robin over the values of `key`, so no company dominates."""
    groups: dict[str, list] = defaultdict(list)
    for r in rows:
        groups[r[key]].append(r)
    for g in groups.values():
        rng.shuffle(g)
    out: list[dict] = []
    while len(out) < n and any(groups.values()):
        for k in sorted(groups):
            if groups[k] and len(out) < n:
                out.append(groups[k].pop())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--assessments', type=int, default=300)
    ap.add_argument('--recommendations', type=int, default=60)
    a = ap.parse_args()
    rng = random.Random(SEED)
    dossier = {r['id']: r for r in json.load(open(ROOT / 'data/dossier/evidence.json'))['records']}

    assessments, recs, cases_seen = [], [], {}
    seen_pairs: set = set()
    for (split, arm), path in RUNS.items():
        cases = {c['id']: c for c in json.load(open(ROOT / CASES[split]))['cases']}
        for rec in json.load(open(ROOT / path))['records']:
            run = f'{split}/{arm}/{rec["case"]}/{rec["attempt"]}'
            cases_seen.setdefault(rec['case'], (split, cases[rec['case']]))
            for x in rec['assessments']:
                src, theory = dossier.get(x['evidence_id']), rec['theories'].get(x['theory_id'], {})
                if not src or not x.get('quote') or (x['evidence_id'], x['quote'], theory.get('claim')) in seen_pairs:
                    continue
                seen_pairs.add((x['evidence_id'], x['quote'], theory.get('claim')))
                assessments.append({'company': rec['company'], 'run': run, 'source_title': src.get('title', ''),
                                    'published_by': 'the company' if src.get('type') == 'company_claim' else 'a third party',
                                    'url': src.get('url', ''), 'quote': x['quote'], 'theory': theory.get('claim', ''),
                                    'agent_kind': x['evidence_kind'], 'agent_direction': x['direction'],
                                    'dossier_kind': src.get('kind')})
            if rec['stop_reason'] == 'finished' and rec.get('final'):
                f = rec['final']
                recs.append({'company': rec['company'], 'run': run, 'question': cases[rec['case']]['question'],
                             'favoured_theory': rec['theories'].get((rec.get('position') or {}).get('favoured_theory', ''), {}).get('claim', ''),
                             'recommendation': f.get('recommendation', ''), 'target_customer': f.get('target_customer', ''),
                             'cited': '; '.join(f'{e}' for e in (f.get('evidence_ids') or f.get('cited') or []))})

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    key: dict = {'assessments': [], 'tests': [], 'recommendations': []}

    rows = even_sample(assessments, 'company', a.assessments, rng)
    with open(out / 'assessments.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['row', 'company', 'source', 'published_by', 'url', 'quote', 'theory', 'LABEL evidence_kind', 'LABEL direction', 'LABEL more than one kind defensible (y/n)', 'notes'])
        for i, r in enumerate(rows):
            w.writerow([i, r['company'], r['source_title'], r['published_by'], r['url'], r['quote'], r['theory'], '', '', '', ''])
            key['assessments'].append({'row': i, 'run': r['run'], 'agent_kind': r['agent_kind'], 'agent_direction': r['agent_direction'], 'dossier_kind': r['dossier_kind']})

    with open(out / 'tests.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['row', 'company', 'question', 'brief', 'test budget (EUR)', 'max weeks', 'LABEL propose or decline', 'LABEL why (one line)', 'notes'])
        for i, (cid, (split, c)) in enumerate(sorted(cases_seen.items())):
            w.writerow([i, c['company'], c['question'], c['brief'], c.get('test_budget'), c.get('max_test_weeks'), '', '', ''])
            key['tests'].append({'row': i, 'case': cid, 'split': split, 'test_warranted': c['test_warranted']})

    rows = even_sample(recs, 'company', a.recommendations, rng)
    with open(out / 'recommendations.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['row', 'company', 'question', 'favoured explanation', 'recommendation', 'target customer', 'LABEL quality 0-3', 'LABEL unsupported claims (quote them)', 'LABEL would you act on it (y/n/with changes)', 'notes'])
        for i, r in enumerate(rows):
            w.writerow([i, r['company'], r['question'], r['favoured_theory'], r['recommendation'], r['target_customer'], '', '', '', ''])
            key['recommendations'].append({'row': i, 'run': r['run']})

    (out / 'key.json').write_text(json.dumps(key, indent=1))
    print({k: len(v) for k, v in key.items()}, 'written to', out)


if __name__ == '__main__':
    main()
