"""Does a decision request with the adapters off leave the next agent request untouched? Asks one agent question (a
training row's context) with every adapter at scale 1, then a decision-style question with every adapter at scale 0,
then the agent question again, and requires the two agent answers' first-token log-probabilities to be identical. Also
reports whether scale 0 and scale 1 differ at all, so the check is not passing on an adapter that does nothing.
Exits 1 if the agent answers differ.

Usage: python adapter_isolation.py --url http://127.0.0.1:PORT --rows final.jsonl
"""

import argparse
import json
import sys
import urllib.request


def post(url: str, body: dict) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())


def first_token(url: str, messages: list[dict], scale: float, adapters: int) -> list[list]:
    body = {
        'messages': messages,
        'temperature': 0,
        'seed': 7,
        'max_tokens': 1,
        'logprobs': True,
        'top_logprobs': 10,
        'lora': [{'id': i, 'scale': scale} for i in range(adapters)],
    }
    top = post(url + '/v1/chat/completions', body)['choices'][0]['logprobs']['content'][0]['top_logprobs']
    return [[t['token'], round(t['logprob'], 6)] for t in top]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--rows', required=True)
    args = parser.parse_args()
    with urllib.request.urlopen(args.url + '/lora-adapters', timeout=60) as response:
        adapters = len(json.load(response))
    with open(args.rows) as handle:
        row = json.loads(handle.readline())
    agent = row['messages'][: row['target_index']]
    decision = [
        {'role': 'user', 'content': 'Classify the passage "Sales rose 4% last year." A. regulation B. market_fact. Answer with the letter only.\nAnswer:'}
    ]
    before = first_token(args.url, agent, 1.0, adapters)
    first_token(args.url, decision, 0.0, adapters)
    after = first_token(args.url, agent, 1.0, adapters)
    base = first_token(args.url, agent, 0.0, adapters)
    report = {'adapters': adapters, 'agent_unchanged': before == after, 'adapter_changes_output': base != before, 'before': before[:3], 'after': after[:3]}
    print(json.dumps(report))
    if not report['agent_unchanged']:
        sys.exit(1)


if __name__ == '__main__':
    main()
