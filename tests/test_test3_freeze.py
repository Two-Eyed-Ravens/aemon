"""Test set 3 (Stage 2): frozen before any run, unseen by development, training and the two earlier test sets."""

import json

from aemon.common.paths import DOCS
from aemon.data.freeze import digest
from aemon.environment.cases import load_cases


def test_test_set_3_is_frozen() -> None:
    frozen = json.loads((DOCS / 'test3_freeze.json').read_text())
    assert digest('cases_heldout3.json')['digest'] == frozen['digest']


def test_no_other_split_sees_test_set_3() -> None:
    test3 = load_cases(split='heldout3')
    scopes = {r.scope for c in test3 for r in c.dossier.records.values()}
    others = load_cases() + load_cases(split='heldout') + load_cases(split='heldout2')
    for case in others:
        assert not scopes & {r.scope for r in case.dossier.records.values()}
    assert not {c.company for c in others} & {c.company for c in test3}
    assert len({c.company for c in test3}) == 12
    assert len(test3) == 48
