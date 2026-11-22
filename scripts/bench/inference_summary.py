"""Inference cost of the fine-tuned agent per serving setting (DECISIONS 19 November, inference cost bench).

For each setting (weights precision, investigations served at once): investigations per GPU hour from the measured wall
time, cost per investigation at the GPU prices of version 1's cost table (reports/cost/roi.json), against Claude Haiku
5.5's measured cost, the share of prompt tokens the server took from its cache instead of computing, and the quality columns that need no
judge (finished runs, refused calls), since a faster setting only counts if it does not finish fewer runs.

Usage: python inference_summary.py --timings bench_timings.jsonl --out bench.json
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

# Claude Haiku 5.5 through the same environment on both test sets: 120 investigations, $1.06 with caching
# (docs/PUBLIC_README.md, cost section); roi.json holds only its list-price estimate
HAIKU_MEASURED_USD = 0.0084


@dataclass
class Setting:
    precision: str
    slots: int
    runs: int
    finished: int
    refused_calls: int
    wall_seconds: float
    investigations_per_gpu_hour: float
    usd_per_investigation: dict[str, float]
    usd_per_finished_investigation: float | None
    prompt_tokens_per_investigation: float
    prompt_share_from_cache: float | None
    completion_tokens_per_investigation: float


def setting(entry: dict, prices: dict[str, float]) -> Setting:
    records = json.loads(Path(entry['report']).read_text())['records']
    runs = len(records)
    finished = sum(r['stop_reason'] == 'finished' for r in records)
    turns = [t for r in records for t in r['model_turns']]
    prompt = sum(t.get('prompt_tokens') or 0 for t in turns)
    processed = [t['prompt_processed'] for t in turns if t.get('prompt_processed') is not None]
    per_hour = runs / entry['wall_seconds'] * 3600
    usd = {name: round(price / per_hour, 5) for name, price in prices.items()}
    median_price = next(iter(prices.values()))
    return Setting(
        precision=entry['precision'],
        slots=entry['slots'],
        runs=runs,
        finished=finished,
        refused_calls=sum(not c.get('accepted') for r in records for c in r['calls'] if not c.get('harness')),
        wall_seconds=entry['wall_seconds'],
        investigations_per_gpu_hour=round(per_hour, 1),
        usd_per_investigation=usd,
        usd_per_finished_investigation=round(median_price / per_hour * runs / finished, 5) if finished else None,
        prompt_tokens_per_investigation=round(prompt / runs),
        prompt_share_from_cache=round(1 - sum(processed) / prompt, 3) if processed and len(processed) == len(turns) else None,
        completion_tokens_per_investigation=round(sum(t.get('completion_tokens') or 0 for t in turns) / runs),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    # the GPU prices behind the self-hosted rows of the version 1 cost table, per hour
    prices = {'A100 40GB median $1.76/h': 1.76, 'low $0.89/h': 0.89, 'hyperscaler $3.67/h': 3.67}
    haiku = HAIKU_MEASURED_USD
    with open(args.timings) as handle:
        entries = [json.loads(line) for line in handle]
    settings = [setting(e, prices) for e in entries if Path(e['report']).exists()]
    Path(args.out).write_text(json.dumps({'haiku_measured_usd_per_investigation': haiku, 'settings': [asdict(s) for s in settings]}, indent=1))
    print(f'Claude Haiku 5.5, measured: ${haiku} per investigation')
    print('| Precision | At once | Finished | Refused | Per GPU hour | $ per investigation (median GPU) | Prompt from cache |')
    print('|---|---|---|---|---|---|---|')
    for s in settings:
        cache = '' if s.prompt_share_from_cache is None else f'{s.prompt_share_from_cache:.0%}'
        print(
            f'| {s.precision} | {s.slots} | {s.finished}/{s.runs} | {s.refused_calls} | {s.investigations_per_gpu_hour} | {s.usd_per_investigation["A100 40GB median $1.76/h"]} | {cache} |'
        )


if __name__ == '__main__':
    main()
