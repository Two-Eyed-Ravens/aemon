"""Checks on test set 3 before it is frozen (DECISIONS 19 November 21:20): leakage and searchability.

Leakage: no test set 3 company name, scope or record id appears in any other case file, in any training-row file, or in
the teacher reports; and no case id of it appears in any run report on disk. Searchability: for each case, queries of
the kind the agent writes (modelled on its searches in the development screens, with the company's short name as its
sources write it), through the dossier's own search at three results per query as the tool gives, reach at least one
premise record (what the existing_offering check needs: reading any one of them) and at least four other records, so
a missed record is the agent's failure, not the dossier's. Run with --split heldout2 to compare with test set 2.
Exits 1 if any check fails.

Usage: python test3_checks.py [--teacher-reports DIR]
"""

import argparse
import json
import sys
from pathlib import Path

from aemon.common.constants.pipeline import TEST_CASE_FILES
from aemon.environment.cases import load_cases
from aemon.environment.tools import Case

ROOT = Path(__file__).resolve().parents[2]
DOSSIER = ROOT / 'data' / 'dossier'
# modelled on the agent's own searches in the development screens (experiments/screen/aya-expanse-8b-prompted_guards.json)
QUERIES = (
    "{company}'s existing product offerings to individual buyers",
    '{company} current market reach, individual consumer buying habits',
    "{company}'s brand perception among individual buyers, customer satisfaction",
    '{company} products, customers and sales channels',
    '{company} consumer products, retail and online shop',
    '{company} company size, revenue and employees',
)
# calibrated on the earlier test sets: the hand-built first test reaches 5 or more everywhere, test set 2 at least 4
MIN_OTHER_REACHED = 4
LEGAL = {'ag', 'se', 'kg', 'gmbh', 'co.', 'kgaa', '&', 'plc', 'inc.', 'limited', 'company', 'group', 'gruppe', 'corporation'}


def short_name(case: Case) -> str:
    """The word of the company's name its own records use most, so 'U.I. Lapp GmbH' is searched as 'Lapp'."""
    texts = ' '.join(r.title + ' ' + r.excerpt for r in case.dossier.records.values()).lower()
    words = [w for w in case.company.split() if w.lower() not in LEGAL and len(w.strip('.')) > 2]
    return max(words, key=lambda w: texts.count(w.lower())) if words else case.company


def needles() -> dict[str, set[str]]:
    data = json.loads((DOSSIER / TEST_CASE_FILES['heldout3']).read_text())
    scopes = {c['scope'] for c in data['cases']}
    records = json.loads((DOSSIER / 'evidence.json').read_text())['records']
    return {
        'company': {c['company'] for c in data['cases']},
        'scope': scopes,
        'record': {r['id'] for r in records if r['scope'] in scopes},
        'case': {c['id'] for c in data['cases']},
    }


def found_in(path: Path, words: set[str]) -> set[str]:
    text = path.read_text(errors='replace')
    return {w for w in words if w in text}


def leakage(teacher_reports: Path | None) -> list[str]:
    found = needles()
    problems = []
    others = [DOSSIER / 'cases.json', *(DOSSIER / f for s, f in TEST_CASE_FILES.items() if s != 'heldout3')]
    rows = sorted((ROOT / 'rows').glob('*.jsonl'))
    reports = sorted(teacher_reports.glob('*.json')) if teacher_reports else []
    for path in [*others, *rows, *reports]:
        hits = found_in(path, found['company'] | found['record'] | found['case'])
        if hits:
            problems.append(f'{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {sorted(hits)[:5]}')
    for path in sorted((ROOT / 'experiments').rglob('*.json')) + sorted((ROOT / 'reports').rglob('*.json')):
        hits = found_in(path, found['case'])
        if hits:
            problems.append(f'run report mentions test set 3 cases: {path.relative_to(ROOT)}')
    return problems


def searchability(split: str) -> list[str]:
    problems = []
    for case in load_cases(split=split):
        name = short_name(case)
        reached: set[str] = set()
        for query in QUERIES:
            reached |= {r.id for r in case.dossier.search(query.format(company=name))}
        premises = [p for p in case.premise_records if p in reached]
        others = reached - set(case.premise_records)
        if (case.premise_records and not premises) or len(others) < MIN_OTHER_REACHED:
            problems.append(f'{case.id} ({name}): premise records reached {premises}; {len(others)} other records reached')
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--teacher-reports', type=Path)
    parser.add_argument('--split', default='heldout3', choices=tuple(TEST_CASE_FILES))
    args = parser.parse_args()
    leaks = leakage(args.teacher_reports) if args.split == 'heldout3' else []
    unsearchable = searchability(args.split)
    print(json.dumps({'leakage': leaks, 'searchability': unsearchable}, indent=1))
    if leaks or unsearchable:
        sys.exit(1)


if __name__ == '__main__':
    main()
