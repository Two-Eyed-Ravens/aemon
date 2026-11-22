"""Checks test set 3's signed what-if pairs, as reviews/heldout_shocks/validate.py did for the final test: each company
has exactly one supports and one undermines case; the two share the simulated record's id and title (neutral metadata);
counts are mirrored with 400 per arm; the excerpt says it is simulated; the targets pick out a theory built from the
spec's relevant claim and not its unrelated one; and the tools refuse the record as support for a theory and as cited
evidence in finish. Prints the checks and exits 1 if any fails. Usage: python reviews/heldout3_shocks/validate.py
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from aemon.environment.cases import load_cases
from aemon.environment.checks import _affected
from aemon.environment.tools import Investigation

SPECS = Path(__file__).with_name('specs.json')


def main() -> None:
    specs = json.loads(SPECS.read_text())['pairs']
    raw = json.loads((Path(__file__).resolve().parents[2] / 'data' / 'dossier' / 'cases_heldout3.json').read_text())['cases']
    cases = load_cases(split='heldout3')
    checks: dict[str, bool] = {}
    for scope, spec in specs.items():
        pair = [c for c in raw if c['scope'] == scope and c.get('shock', {}).get('direction') in ('supports', 'undermines')]
        checks[f'{scope}: one supports and one undermines'] = len(pair) == 2 and {c['shock']['direction'] for c in pair} == {'supports', 'undermines'}
        if len(pair) != 2:
            continue
        a, b = pair
        checks[f'{scope}: same record id and title'] = (
            a['shock']['record']['id'] == b['shock']['record']['id'] and a['shock']['record']['title'] == b['shock']['record']['title']
        )
        da, db = a['shock']['design'], b['shock']['design']
        checks[f'{scope}: mirrored counts, 400 per arm'] = (
            da['treatment_count'] == db['control_count'] and da['control_count'] == db['treatment_count'] and da['treatment_n'] == db['treatment_n'] == 400
        )
        checks[f'{scope}: excerpt says simulated'] = all(c['shock']['record']['excerpt'].startswith('SIMULATED RESULT, NOT REAL DATA.') for c in pair)
        for case in [c for c in cases if c.id in {a['id'], b['id']}]:
            run = SimpleNamespace(
                case=case,
                theories={
                    'T1': {'first_claim': spec['relevant'], 'why_behaviour_changes': ''},
                    'T2': {'first_claim': spec['unrelated'], 'why_behaviour_changes': ''},
                },
            )
            checks[f'{case.id}: targets pick out the relevant theory only'] = _affected(run) == ['T1']
            inv = Investigation(case)
            inv.frame = {'objective': 'test'}
            inv.theories = {'T1': {}}
            inv.shock_delivered = True
            inv.surfaced.add(case.shock.id)
            inv.read.add(case.shock.id)
            assessed = inv.call(
                'assess_evidence',
                {
                    'theory_id': 'T1',
                    'evidence_id': case.shock.id,
                    'direction': 'supports',
                    'quote': 'SIMULATED RESULT, NOT REAL DATA.',
                    'evidence_kind': 'independent_study',
                    'does_not_show': 'No real-world demand is demonstrated.',
                },
            )
            checks[f'{case.id}: refused as support'] = 'error' in assessed and inv.calls[-1]['category'] == 'synthetic_as_evidence'
            finished = inv.call(
                'finish',
                {
                    'recommendation': 'test',
                    'target_customer': 'test',
                    'value_proposition': 'test',
                    'favoured_theory': 'T1',
                    'next_action': 'test',
                    'uncertainty': 'test',
                    'would_change_if': ['test'],
                    'evidence_ids': [case.shock.id],
                },
            )
            checks[f'{case.id}: refused as cited evidence'] = 'error' in finished and inv.calls[-1]['category'] == 'synthetic_as_evidence'
    failed = [k for k, v in checks.items() if not v]
    print(json.dumps({'passed': len(checks) - len(failed), 'total': len(checks), 'failed': failed}, indent=1))
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
