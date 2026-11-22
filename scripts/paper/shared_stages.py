"""Is the gain more than finishing? Stage 1's reached-only comparison (scripts/release/robustness.py) on the Stage 2
development results: each pair of runs (same case and attempt) is compared only on the rubric dimensions both runs
were scored on, so a stage one run never reached counts for neither. A packet judged more than once takes the mean of
its judgments per dimension. Reports, per comparison, the full and the shared-stages difference with case-bootstrap
intervals, and how many dimensions the pairs share on average.

Usage: python scripts/paper/shared_stages.py --key KEY.jsonl --predictions PRED.jsonl --compare first,second [...]
"""

import argparse
import json
import random
import statistics
from collections import defaultdict

from aemon.evaluation.judging.report import episode_scores_all, load

BOOTSTRAP = 4000
SEED = 20261106


def scored_dimensions(judgments: list[dict]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for judgment in judgments:
        for name, dimension in judgment['dimensions'].items():
            if dimension['status'] == 'scored':
                values[name].append(dimension['score'])
    return {name: statistics.mean(v) for name, v in values.items()}


def bootstrap(groups: dict[str, list[float]]) -> list[float]:
    names = sorted(groups)
    rng = random.Random(SEED)
    draws = sorted(statistics.mean([x for n in (rng.choice(names) for _ in names) for x in groups[n]]) for _ in range(BOOTSTRAP))
    pooled = statistics.mean(x for v in groups.values() for x in v)
    return [pooled, draws[int(0.025 * BOOTSTRAP)], draws[int(0.975 * BOOTSTRAP) - 1]]


def compare(key: list[dict], predictions: dict, first: str, second: str) -> dict:
    cells: dict[tuple[str, int], dict[str, dict]] = defaultdict(dict)
    for row in key:
        prediction = predictions.get(row['packet_id'])
        if row['arm'] in (first, second) and prediction and prediction['judgments']:
            cells[(row['case'], row['attempt'])][row['arm']] = prediction
    full, shared, counts = defaultdict(list), defaultdict(list), []
    for (case, _), arms in cells.items():
        if first not in arms or second not in arms:
            continue
        a, b = (episode_scores_all(arms[x]['judgments'])[0] for x in (first, second))
        if a is None or b is None:
            continue
        full[case].append(a - b)
        da, db = (scored_dimensions(arms[x]['judgments']) for x in (first, second))
        common = set(da) & set(db)
        if common:
            shared[case].append(statistics.mean(da[n] - db[n] for n in common))
            counts.append(len(common))
    return {
        'arms': f'{first} minus {second}',
        'pairs': sum(map(len, full.values())),
        'full': bootstrap(full),
        'shared_stages': bootstrap(shared),
        'pairs_with_shared_stages': sum(map(len, shared.values())),
        'mean_shared_dimensions': statistics.mean(counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', required=True)
    parser.add_argument('--predictions', required=True)
    parser.add_argument('--compare', action='append', required=True)
    args = parser.parse_args()
    key = [json.loads(line) for line in open(args.key) if line.strip()]
    predictions = load(args.predictions)
    results = [compare(key, predictions, *spec.split(',')) for spec in args.compare]
    for r in results:
        f, s = r['full'], r['shared_stages']
        print(
            f'{r["arms"]:36s} full {f[0]:+.2f} [{f[1]:+.2f}, {f[2]:+.2f}]   shared stages {s[0]:+.2f} [{s[1]:+.2f}, {s[2]:+.2f}]   '
            f'pairs {r["pairs_with_shared_stages"]}/{r["pairs"]}, mean shared dimensions {r["mean_shared_dimensions"]:.1f}'
        )
    print(json.dumps(results))


if __name__ == '__main__':
    main()
