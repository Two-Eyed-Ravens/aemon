"""A condition against its reference pooled over training seeds, as the 19 November rules read it: each run is paired
with the reference run of the same case and attempt at the same training seed, and the interval comes from resampling
whole cases (every seed's and attempt's pairs of a case move together). A packet judged more than once takes the mean
of its judgments.

Usage: uv run python scripts/paper/pooled_seeds.py --key KEY.jsonl --predictions PRED.jsonl \
           --pair ayaB7_guards,ayaA7_guards --pair ayaB11_guards,ayaA11_guards --pair ayaB13_guards,ayaA13_guards
"""

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from aemon.evaluation.judging.report import episode_scores_all, load

BOOTSTRAP = 4000
SEED = 20261121


def run_scores(key: list[dict], predictions: dict) -> dict[tuple[str, str, int], float]:
    """(arm, case, attempt) -> the run's judged score, for every run with a valid judgment."""
    scores = {}
    for row in key:
        prediction = predictions.get(row['packet_id'])
        if not prediction or not prediction['judgments']:
            continue
        score, _ = episode_scores_all(prediction['judgments'])
        if score is not None:
            scores[(row['arm'], row['case'], row['attempt'])] = score
    return scores


def paired_by_case(scores: dict, pairs: list[tuple[str, str]]) -> dict[str, list[float]]:
    by_case: dict[str, list[float]] = defaultdict(list)
    for first, second in pairs:
        for (arm, case, attempt), score in scores.items():
            other = scores.get((second, case, attempt))
            if arm == first and other is not None:
                by_case[case].append(score - other)
    return by_case


def bootstrap(by_case: dict[str, list[float]]) -> list[float]:
    cases = sorted(by_case)
    rng = random.Random(SEED)
    draws = []
    for _ in range(BOOTSTRAP):
        sample = [d for case in (rng.choice(cases) for _ in cases) for d in by_case[case]]
        draws.append(statistics.mean(sample))
    draws.sort()
    pooled = statistics.mean(d for v in by_case.values() for d in v)
    return [pooled, draws[int(0.025 * BOOTSTRAP)], draws[int(0.975 * BOOTSTRAP) - 1]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--predictions', required=True)
    parser.add_argument('--pair', action='append', required=True, help='condition,reference at one training seed')
    args = parser.parse_args()
    key = [json.loads(line) for line in args.key.read_text().splitlines() if line.strip()]
    scores = run_scores(key, load(args.predictions))
    pairs = [tuple(spec.split(',')) for spec in args.pair]
    by_case = paired_by_case(scores, pairs)
    mean, low, high = bootstrap(by_case)
    pair_count = sum(map(len, by_case.values()))
    print(json.dumps({'pairs': pair_count, 'cases': len(by_case), 'pooled': [round(mean, 3), round(low, 3), round(high, 3)]}))


if __name__ == '__main__':
    main()
