"""Investigation cases, built from the verified dossier. Filled in once the evidence is checked."""

from __future__ import annotations

import json
from typing import Any

from aemon.common.constants.pipeline import SPLITS, TEST_CASE_FILES
from aemon.common.paths import DOSSIER
from aemon.environment.dossier import Dossier, Record
from aemon.environment.tools import Case


def load_cases(selection: str = 'all', split: str = 'development') -> list[Any]:
    """Development cases by default. Held-out cases load only when asked for by name (TEST_CASE_FILES): 'heldout' is the
    final test, 'heldout2' the second test set and 'heldout3' the third (Stage 2); nothing trains on any of them."""
    if split not in SPLITS:
        raise ValueError(f'unknown split {split!r}: one of {SPLITS}')
    name = TEST_CASE_FILES.get(split, 'cases.json')
    data = json.loads((DOSSIER / name).read_text())
    records = Dossier.load(DOSSIER / 'evidence.json')
    cases = []
    for item in data['cases']:
        if selection != 'all' and item['id'] not in selection.split(','):
            continue
        shock = item.get('shock')
        record = Record(**{**shock['record'], 'bears_on': ()}) if shock else None
        shared = tuple(item.get('shared_scopes', ['market']))  # the hearing-protection market evidence belongs to the original three only
        visible = Dossier([r for r in records if r.scope in (*shared, item['scope'])])
        cases.append(
            Case(
                item['id'],
                item['company'],
                item['question'],
                item['brief'],
                item['search_budget'],
                item['test_budget'],
                item['max_test_weeks'],
                visible,
                record,
                tuple(shock['targets']) if shock else (),
                shock.get('direction', 'undermines') if shock else 'undermines',
                bool(item.get('simulated')),
                tuple(item.get('premise_records', ())),
                item.get('test_warranted', True),
            )
        )
    return cases
