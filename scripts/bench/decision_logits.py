"""Zero-training decision model: answer each typed sub-decision by reading the option letters' log-probabilities at the
first reply token (the first step of arXiv 2610.17205), and compare with the agent's own choices in the saved runs.

Confidence is the letter probabilities renormalised over the options. Reports accuracy, recall per class, expected
calibration error (10 equal-width bins), accuracy when abstaining below a confidence threshold, and the agent's own
accuracy and the majority-class baseline on the same items.

Usage: python decision_logits.py --url http://127.0.0.1:PORT --items decision_items.jsonl --arms base= v1=0 v3=1 --out out.json
(`name=` all adapters at scale 0; `name=i` adapter i at scale 1; as in retention.py, whose helpers this reuses.)
"""

import argparse
import json
import math
from collections import Counter

from retention import post, set_adapters

from aemon.agent import decision

# the same prompts and option order as the decision model inside the agent loop (src/aemon/agent/decision.py)
KINDS = list(decision.KINDS)
LETTERS = decision.LETTERS
TESTS = list(decision.TESTS)


def kind_prompt(it: dict) -> str:
    return decision.kind_prompt(it['title'], it['origin'] == 'company_claim', it['quote'])


def test_prompt(it: dict) -> str:
    return decision.test_prompt(it['question'], it['brief'], it['budget'], it['weeks'])


def letter_probs(base: str, prompt: str, n: int) -> dict[str, float]:
    out = post(base + '/v1/chat/completions', {'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0, 'seed': 7,
                                               'max_tokens': 1, 'logprobs': True, 'top_logprobs': 20,
                                               'chat_template_kwargs': {'enable_thinking': False}})  # ignored by templates without thinking
    scores: dict[str, float] = {}
    for cand in out['choices'][0]['logprobs']['content'][0]['top_logprobs']:
        tok = cand['token'].strip().strip('*').strip()
        if tok in LETTERS[:n]:
            scores[tok] = max(scores.get(tok, -1e9), cand['logprob'])
    if not scores:
        return {}
    z = sum(math.exp(v) for v in scores.values())
    return {k: math.exp(v) / z for k, v in scores.items()}


def ece(conf: list[float], correct: list[bool], bins: int = 10) -> float:
    total, n = 0.0, len(conf)
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [i for i, c in enumerate(conf) if lo < c <= hi or (b == 0 and c == 0)]
        if sel:
            total += len(sel) / n * abs(sum(correct[i] for i in sel) / len(sel) - sum(conf[i] for i in sel) / len(sel))
    return total


def summarise(rows: list[dict], labels: list[str]) -> dict:
    n = len(rows)
    correct = [r['pred'] == r['gold'] for r in rows]
    conf = [r['conf'] for r in rows]
    recall = {lab: (sum(1 for r in rows if r['gold'] == lab and r['pred'] == lab) / g if (g := sum(r['gold'] == lab for r in rows)) else None)
              for lab in labels}
    abstain = {}
    for t in (0.5, 0.7, 0.9):
        kept = [c for c, p in zip(correct, conf, strict=True) if p >= t]
        abstain[str(t)] = {'coverage': len(kept) / n, 'accuracy': sum(kept) / len(kept) if kept else None}
    return {'n': n, 'accuracy': sum(correct) / n, 'recall': recall, 'ece': ece(conf, correct),
            'no_letter': sum(r['pred'] is None for r in rows), 'abstain': abstain}


def agent_baseline(items: list[dict]) -> dict:
    out: dict = {}
    for task in ('evidence_kind', 'test_choice'):
        sel = [i for i in items if i['task'] == task]
        golds = Counter(i['gold'] for i in sel)
        out[task] = {'items': len(sel), 'majority_class': golds.most_common(1)[0][0],
                     'majority_accuracy': golds.most_common(1)[0][1] / len(sel), 'agent': {}}
        for arm in ('version 1', 'final system'):
            inst = [(c, i['gold']) for i in sel for c in i['agent'].get(arm, [])]
            per_item = [sum(c == i['gold'] for c in i['agent'][arm]) / len(i['agent'][arm]) for i in sel if i['agent'].get(arm)]
            out[task]['agent'][arm] = {'choices': len(inst), 'accuracy_over_choices': sum(c == g for c, g in inst) / len(inst),
                                       'accuracy_per_item': sum(per_item) / len(per_item),
                                       'choices_by_value': dict(Counter(c for c, _ in inst))}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', required=True)
    ap.add_argument('--items', required=True)
    ap.add_argument('--arms', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    items = [json.loads(line) for line in open(a.items)]
    result: dict = {'agent_baseline': agent_baseline(items), 'arms': {}, 'rows': {}}
    for spec in a.arms:
        name, _, idx = spec.partition('=')
        set_adapters(a.url, int(idx) if idx else None)
        rows = []
        for it in items:
            if it['task'] == 'evidence_kind':
                probs, opts = letter_probs(a.url, kind_prompt(it), 6), KINDS
            else:
                probs, opts = letter_probs(a.url, test_prompt(it), 2), TESTS
            if probs:
                best = max(probs, key=lambda k: probs[k])
                pred, conf = opts[LETTERS.index(best)], probs[best]
            else:
                pred, conf = None, 0.0
            rows.append({'id': it['id'], 'task': it['task'], 'gold': it['gold'], 'pred': pred, 'conf': conf,
                         'probs': {opts[LETTERS.index(k)]: v for k, v in probs.items()}})
        result['rows'][name] = rows
        result['arms'][name] = {'evidence_kind': summarise([r for r in rows if r['task'] == 'evidence_kind'], KINDS),
                                'test_choice': summarise([r for r in rows if r['task'] == 'test_choice'], TESTS)}
        print(name, json.dumps({t: {'accuracy': round(v['accuracy'], 3), 'ece': round(v['ece'], 3)} for t, v in result['arms'][name].items()}), flush=True)
    json.dump(result, open(a.out, 'w'), indent=1)
    print(json.dumps({'agent_baseline': result['agent_baseline'], 'arms': result['arms']}, indent=1))


if __name__ == '__main__':
    main()
