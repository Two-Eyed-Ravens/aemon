"""Adds the signed what-if pairs in specs.json to test set 3 (data/dossier/cases_heldout3.json), before it is frozen.

For each company with a spec: a `-new-evidence-favours-<topic>` case (direction supports, 72 against 32 of 400 per arm)
and a `-new-evidence-undermines-<topic>` case (counts reversed), both copies of the company's base case with one shared
simulated record `SYN-<SCOPE>-UPDATE` whose id and title are identical, so nothing but the counts tells them apart.
Re-running replaces a company's pair. Usage: python reviews/heldout3_shocks/build.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'data' / 'dossier' / 'cases_heldout3.json'
SPECS = Path(__file__).with_name('specs.json')
N = 400
HIGH, LOW = 72, 32
PREFIX = 'SIMULATED RESULT, NOT REAL DATA. No study was conducted. Treat this as a what-if only.'


def record(scope: str, spec: dict, treatment: int, control: int) -> dict:
    excerpt = ' '.join(
        (
            PREFIX,
            spec['setup'],
            f'The outcome was a {spec["outcome"]} among all {N} assigned people per arm.',
            spec['result'].format(treatment=treatment, control=control),
            spec['limits'],
        )
    )
    return {
        'id': f'SYN-{scope.upper()}-UPDATE',
        'type': 'synthetic',
        'title': spec['title'],
        'url': 'n/a',
        'date': 'n/a',
        'excerpt': excerpt,
        'access_limitation': 'Entirely hypothetical case-author construction; no study was conducted.',
        'scope': scope,
        'geography': 'hypothetical; not specified',
        'population': spec['population'],
    }


def variant(base: dict, scope: str, spec: dict, direction: str) -> dict:
    treatment, control = (HIGH, LOW) if direction == 'supports' else (LOW, HIGH)
    word = 'favours' if direction == 'supports' else 'undermines'
    design = {
        'pair_id': f'{scope}-{spec["topic"]}-v1',
        'target_mechanism': spec['mechanism'],
        'assignment': f'randomized {N} per arm',
        'outcome': spec['outcome'],
        'treatment_count': treatment,
        'control_count': control,
        'treatment_n': N,
        'control_n': N,
        'observed_risk_difference': round((treatment - control) / N, 3),
        'interpretation': f'directional evidence about {spec["mechanism"]} only; no required business recommendation reversal',
        'status': 'pre-evaluation, test set 3',
    }
    shock = {'record': record(scope, spec, treatment, control), 'targets': spec['targets'], 'direction': direction, 'design': design}
    return dict(base, id=f'{scope}-new-evidence-{word}-{spec["topic"]}', shock=shock)


def main() -> None:
    specs = json.loads(SPECS.read_text())['pairs']
    data = json.loads(CASES.read_text())
    data['cases'] = [c for c in data['cases'] if not (c['scope'] in specs and c.get('shock', {}).get('direction') in ('supports', 'undermines'))]
    added = []
    for scope, spec in specs.items():
        base = next(c for c in data['cases'] if c['id'] == f'{scope}-base')
        for direction in ('supports', 'undermines'):
            made = variant(base, scope, spec, direction)
            data['cases'].append(made)
            added.append(made['id'])
    CASES.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'added': added, 'cases': len(data['cases'])}, indent=1))


if __name__ == '__main__':
    main()
