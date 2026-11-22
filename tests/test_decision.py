"""The decision model inside the agent loop (src/aemon/agent/decision.py, decide_kind): when it decides, abstains,
stays out of the way, and how its change is recorded and replayed."""

import json

import pytest

from aemon.agent import decision
from aemon.agent.decision import KINDS, Decision, KindDecider, decide
from aemon.agent.loop import play
from aemon.agent.tool_schemas import TOOL_SCHEMA
from aemon.common.constants.env import EVIDENCE_KINDS
from aemon.common.constants.prompts import PROMPTS
from aemon.environment.cases import load_cases
from aemon.environment.tools import Case, Investigation

CASE = 'hellberg-new-evidence-looks'
THEORY = {
    'claim': 'Wearers who find protectors uncomfortable take them off, so a comfortable design is worn more.',
    'who_benefits': 'workers',
    'why_behaviour_changes': 'comfort',
    'how_value_is_captured': 'premium price',
    'assumptions': ['comfort drives wear time'],
    'predictions': ['wear time rises with comfort'],
}


def case() -> Case:
    return next(c for c in load_cases() if c.id == CASE)


def third_party_quote() -> tuple[str, str]:
    """A third-party source the first search surfaces, and a sentence of it the tools accept as a quote."""
    run = Investigation(case())
    run.call('read_brief', {})
    run.call('frame_problem', {'objective': 'Decide', 'constraints': ['budget'], 'alternatives': ['enter', 'do not enter']})
    for hit in run.call('search_evidence', {'query': 'hearing protection comfort wearers'})['results']:
        source = run._source(hit['id'])
        if source.type != 'company_claim':
            sentence = max(source.excerpt.split('. '), key=len).rstrip('.')
            return hit['id'], sentence
    raise AssertionError('no third-party source in the first search')


def turns_to_assessment(evidence_id: str, quote: str, kind: str) -> list[str]:
    calls = [
        {'name': 'read_brief', 'arguments': {}},
        {'name': 'frame_problem', 'arguments': {'objective': 'Decide', 'constraints': ['budget'], 'alternatives': ['enter', 'do not enter']}},
        {'name': 'search_evidence', 'arguments': {'query': 'hearing protection comfort wearers'}},
        {'name': 'read_source', 'arguments': {'id': evidence_id}},
        {'name': 'add_theory', 'arguments': THEORY},
        {
            'name': 'assess_evidence',
            'arguments': {
                'theory_id': 'T1',
                'evidence_id': evidence_id,
                'direction': 'neutral',
                'quote': quote,
                'evidence_kind': kind,
                'does_not_show': 'whether buyers would pay more',
            },
        },
    ]
    return [json.dumps(c) for c in calls]


def test_the_kind_list_offered_is_the_environments() -> None:
    assert set(KINDS) == set(EVIDENCE_KINDS)


def test_a_confident_score_over_every_option_decides() -> None:
    made = decide({'A': -3.0, 'B': -0.01}, ('propose', 'decline'), 0.9)
    assert made.choice == 'decline' and made.confidence > 0.9


def test_a_missing_option_or_low_confidence_abstains() -> None:
    assert decide({'A': -0.01}, ('propose', 'decline'), 0.9).abstained
    unsure = decide({'A': -0.7, 'B': -0.7}, ('propose', 'decline'), 0.9)
    assert unsure.abstained and unsure.confidence == pytest.approx(0.5)


def test_a_confident_decision_replaces_the_kind_and_replay_reproduces_it(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence_id, quote = third_party_quote()
    market_fact = 'ABCDEF'[KINDS.index('market_fact')]
    monkeypatch.setattr(decision, 'letter_logprobs', lambda url, prompt, lora: {letter: (-0.001 if letter == market_fact else -9.0) for letter in 'ABCDEF'})
    texts = iter(turns_to_assessment(evidence_id, quote, 'independent_study'))
    decider = KindDecider('http://unused', adapters=1)
    run, info = play(
        case(), lambda *a, **k: {'text': next(texts)}, PROMPTS['plain'], 6, 4, 100, False, TOOL_SCHEMA, recovery_features=('decide_kind',), decide=decider
    )
    assessed = run.assessments[-1]
    assert assessed['evidence_kind'] == 'market_fact'
    turn = info['turns'][-1]
    assert json.loads(turn['text'])['arguments']['evidence_kind'] == 'independent_study'  # the model's own text is kept
    assert turn['decision']['applied'] and turn['decision']['agent'] == 'independent_study'
    assert run.calls[-1]['decision'] == turn['decision']
    replayed, _ = play(case(), lambda *a, **k: {'text': ''}, PROMPTS['plain'], 0, 4, 100, False, TOOL_SCHEMA, prefix=info['turns'])
    assert replayed.assessments[-1]['evidence_kind'] == 'market_fact'


def test_an_abstention_leaves_the_call_and_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence_id, quote = third_party_quote()
    monkeypatch.setattr(decision, 'letter_logprobs', lambda url, prompt, lora: {letter: -1.8 for letter in 'ABCDEF'})
    texts = iter(turns_to_assessment(evidence_id, quote, 'independent_study'))
    run, info = play(
        case(),
        lambda *a, **k: {'text': next(texts)},
        PROMPTS['plain'],
        6,
        4,
        100,
        False,
        TOOL_SCHEMA,
        recovery_features=('decide_kind',),
        decide=KindDecider('http://unused', 1),
    )
    assert run.assessments[-1]['evidence_kind'] == 'independent_study'
    assert info['turns'][-1]['decision']['applied'] is False and info['turns'][-1]['decision']['decided'] is None


def test_a_company_claim_under_evidence_first_is_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    run = Investigation(case())
    run.recovery = frozenset({'evidence_first', 'decide_kind'})
    run.call('read_brief', {})
    run.call('frame_problem', {'objective': 'Decide', 'constraints': ['budget'], 'alternatives': ['enter', 'do not enter']})
    hits = run.call('search_evidence', {'query': 'hearing protection comfort wearers'})['results']
    claim = next(h['id'] for h in hits if run._source(h['id']).type == 'company_claim')
    run.call('read_source', {'id': claim})

    def never(*args: object) -> dict[str, float]:
        raise AssertionError('the decision model was asked about a single-option kind')

    monkeypatch.setattr(decision, 'letter_logprobs', never)
    call = {'name': 'assess_evidence', 'arguments': {'evidence_id': claim, 'quote': 'x', 'evidence_kind': 'company_assertion'}}
    assert KindDecider('http://unused', 1)(run, call) == (call, None)


def test_decide_kind_without_a_decision_model_is_refused() -> None:
    with pytest.raises(ValueError):
        play(case(), lambda *a, **k: {'text': ''}, PROMPTS['plain'], 1, 4, 100, False, TOOL_SCHEMA, recovery_features=('decide_kind',))


def test_decision_is_a_plain_record() -> None:
    assert Decision(None, 0.0).abstained
