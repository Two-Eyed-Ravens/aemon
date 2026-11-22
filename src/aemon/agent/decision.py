"""A decision model for the agent's typed choices: the option letters' log-probabilities at the first reply token, read
from the base weights (the adapter at scale 0 for that one request, since the adapters make this readout worse; DECISIONS
18 November), with an abstain route. First step of arXiv 2610.17205, used inside the agent loop by `decide_kind`.

The confidence is the probability of the best option renormalised over all the options, and only when every option's
letter is among the returned candidates: a partial set would make the confidence look higher than it is, so it abstains.
"""

from __future__ import annotations

import json
import math
import os
import urllib.request
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aemon.agent.backends.llama_client import headers
from aemon.common.types import Json

if TYPE_CHECKING:
    from aemon.environment.tools import Investigation

LETTERS = 'ABCDEF'
# the order the letters are offered in, as in the offline measurement (reports/decision_logits/)
KINDS = ('regulation', 'independent_study', 'customer_observation', 'company_assertion', 'analogy', 'market_fact')
KIND_TEXT = {
    'regulation': "a law, standard, certification, official approval or ruling, or an authority's recommendation",
    'independent_study': "the result of formal research or testing by a party with no stake (a published study, a government or laboratory test, a consumer-testing organisation's ratings)",
    'customer_observation': 'what customers or users did, bought, said or complained about, including user reviews and survey results about customers',
    'company_assertion': 'the company or its people describing itself, its products, intentions, plans or performance, whether published by the company or quoted by someone else',
    'analogy': 'a different company, product, market or period, offered as a parallel to this decision',
    'market_fact': 'any other fact about the market, product, technology, channel, history or finances reported as fact',
}
TESTS = ('propose', 'decline')
DEFAULT_THRESHOLD = 0.9


@dataclass
class Decision:
    choice: str | None
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def abstained(self) -> bool:
        return self.choice is None


def kind_prompt(title: str, company_published: bool, quote: str, options: tuple[str, ...] = KINDS) -> str:
    origin = 'the company itself' if company_published else 'a third party'
    lines = [
        'Classify what the quoted passage establishes. Decide from the claim in the quote, using the first option that fits, in this order.',
        '',
        f'Source: {title} (published by {origin})',
        f'Quote: "{quote}"',
        '',
    ]
    lines += [f'{letter}. {kind}: {KIND_TEXT[kind]}' for letter, kind in zip(LETTERS, options, strict=False)]
    lines += ['', 'Answer with the letter only.', 'Answer:']
    return '\n'.join(lines)


def test_prompt(question: str, brief: str, budget: int, weeks: int) -> str:
    return '\n'.join(
        [
            'An analyst is investigating a strategy question from public records. Before recommending, should they run a small market test?',
            'A test is worth proposing only if its result could change the decision and it fits the budget and time. Decline it if the decision is already settled by the facts (for example the company cannot act on it), or no test within the limits could tell the explanations apart.',
            '',
            f'Question: {question}',
            f'Brief: {brief}',
            f'Test budget: {budget} euros, at most {weeks} weeks.',
            '',
            'A. Propose a test',
            'B. Decline a test',
            '',
            'Answer with the letter only.',
            'Answer:',
        ]
    )


def letter_logprobs(url: str, prompt: str, lora: list[dict[str, float]] | None) -> dict[str, float]:
    """The best log-probability of each option letter among the first token's top 20 candidates."""
    body: Json = {
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0,
        'seed': 7,
        'max_tokens': 1,
        'logprobs': True,
        'top_logprobs': 20,
        'chat_template_kwargs': {'enable_thinking': False},
    }
    if lora is not None:
        body['lora'] = lora
    request = urllib.request.Request(url + '/v1/chat/completions', data=json.dumps(body).encode(), headers=headers())
    with urllib.request.urlopen(request, timeout=int(os.environ.get('CHAT_TIMEOUT', 300))) as response:
        data = json.load(response)
    best: dict[str, float] = {}
    for candidate in data['choices'][0]['logprobs']['content'][0]['top_logprobs']:
        token = candidate['token'].strip().strip('*').strip()
        if token in LETTERS:
            best[token] = max(best.get(token, -math.inf), candidate['logprob'])
    return best


def decide(logprobs: dict[str, float], options: tuple[str, ...], threshold: float) -> Decision:
    """The best option if every option was scored and its renormalised probability reaches the threshold."""
    letters = LETTERS[: len(options)]
    if any(letter not in logprobs for letter in letters):
        return Decision(None, 0.0)
    total = sum(math.exp(logprobs[letter]) for letter in letters)
    scores = {option: math.exp(logprobs[letter]) / total for letter, option in zip(letters, options, strict=True)}
    best = max(scores, key=lambda option: scores[option])
    if scores[best] < threshold:
        return Decision(None, scores[best], scores)
    return Decision(best, scores[best], scores)


@dataclass
class KindDecider:
    """decide_kind: the evidence kind of an assess_evidence call, from the base weights. adapters is how many LoRA
    adapters the server holds, all switched off for the decision request."""

    url: str
    adapters: int
    threshold: float = DEFAULT_THRESHOLD

    def options_for(self, run: Investigation, evidence_id: str) -> tuple[str, ...]:
        # evidence_first already offers a company's own claim only as a company assertion (recovery.evidence_first)
        if 'evidence_first' in run.recovery and run._source(evidence_id).type == 'company_claim':
            return ('company_assertion',)
        return KINDS

    def __call__(self, run: Investigation, call: Json) -> tuple[Json, Json | None]:
        """The call to execute, and the decision record, or the call unchanged and None when it does not apply."""
        arguments = call.get('arguments')
        if call.get('name') != 'assess_evidence' or not isinstance(arguments, dict):
            return call, None
        evidence_id, quote = arguments.get('evidence_id'), arguments.get('quote')
        if not isinstance(evidence_id, str) or evidence_id not in run.read or not isinstance(quote, str):
            return call, None
        options = self.options_for(run, evidence_id)
        if len(options) < 2:
            return call, None
        source = run._source(evidence_id)
        prompt = kind_prompt(source.title, source.type == 'company_claim', quote, options)
        lora = [{'id': i, 'scale': 0.0} for i in range(self.adapters)] or None
        decision = decide(letter_logprobs(self.url, prompt, lora), options, self.threshold)
        agent = arguments.get('evidence_kind')
        applied = decision.choice is not None and decision.choice != agent
        record = {
            'feature': 'decide_kind',
            'agent': agent,
            'decided': decision.choice,
            'confidence': round(decision.confidence, 4),
            'threshold': self.threshold,
            'applied': applied,
        }
        if not applied:
            return call, record
        executed = {**call, 'arguments': {**arguments, 'evidence_kind': decision.choice}}
        record['executed_arguments'] = executed['arguments']
        return executed, record
