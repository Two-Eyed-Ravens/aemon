"""Test set 3, read exactly as registered (DECISIONS, 20 November: 14:05 point 5, 14:12, and the two-judge entry):

- primary score of a run: the mean of the two judges' run scores (each judge's run score is the mean of its judged
  dimensions, unreached dimensions 0; a packet judged more than once by one judge takes that judge's mean);
- runs a judge could not score validly are listed and left out, never re-judged;
- each comparison is paired by case and attempt; its interval is over companies: a t-interval over the company means
  (Eq. 3 of the paper, t with companies - 1 degrees of freedom), with a company bootstrap and the case bootstrap beside it;
- each judge's own comparison and the judges' agreement are reported, and a sign disagreement between judges on a
  comparison is flagged, not resolved.

Usage: python scripts/test3/analyze.py --key KEY.jsonl --judge codexsol170=PRED.jsonl --judge claudecode=PRED.jsonl \
           --compare A,prompted --compare A,stage1 --out report.json
"""

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import spearmanr
from scipy.stats import t as student_t

from aemon.evaluation.judging.report import episode_scores_all, load

REACHED = 'scored'

BOOTSTRAP = 4000
SEED = 20261123


def run_scores(key: list[dict], path: str) -> tuple[dict[int, float], list[int]]:
    """One judge's score per key row, and the rows it could not score."""
    predictions = load(path)
    scores, missing = {}, []
    for i, row in enumerate(key):
        prediction = predictions.get(row['packet_id'])
        score, _ = episode_scores_all(prediction['judgments']) if prediction else (None, {})
        if score is None:
            missing.append(i)
        else:
            scores[i] = score
    return scores, missing


def percentile_bootstrap(groups: dict[str, list[float]], seed: int) -> list[float]:
    names = sorted(groups)
    rng = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAP):
        sample = [x for name in (rng.choice(names) for _ in names) for x in groups[name]]
        draws.append(statistics.mean(sample))
    draws.sort()
    return [draws[int(0.025 * BOOTSTRAP)], draws[int(0.975 * BOOTSTRAP) - 1]]


def company_t(by_company: dict[str, list[float]]) -> list[float]:
    """Eq. 3: mean of company means plus or minus t(0.975, G-1) times their standard error."""
    means = [statistics.mean(v) for v in by_company.values()]
    g = len(means)
    centre = statistics.mean(means)
    half = student_t.ppf(0.975, g - 1) * statistics.stdev(means) / g**0.5
    return [centre - half, centre + half]


def compare(key: list[dict], scores: dict[int, float], first: str, second: str) -> dict:
    cells: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for i, row in enumerate(key):
        if i in scores and row['arm'] in (first, second):
            cells[(row['case'], row['attempt'])][row['arm']] = scores[i]
    by_case: dict[str, list[float]] = defaultdict(list)
    by_company: dict[str, list[float]] = defaultdict(list)
    unpaired = 0
    for (case, _), arms in cells.items():
        if first in arms and second in arms:
            difference = arms[first] - arms[second]
            by_case[case].append(difference)
            by_company[case.split('-')[0]].append(difference)
        else:
            unpaired += 1
    company_means = {c: statistics.mean(v) for c, v in sorted(by_company.items())}
    return {
        'arms': f'{first} minus {second}',
        'pairs': sum(map(len, by_case.values())),
        'companies': len(by_company),
        'unpaired_runs': unpaired,
        'mean_of_company_means': statistics.mean(company_means.values()),
        'company_t_interval': company_t(by_company),
        'company_bootstrap_interval': percentile_bootstrap(by_company, SEED),
        'pooled_mean': statistics.mean(x for v in by_case.values() for x in v),
        'case_bootstrap_interval': percentile_bootstrap(by_case, SEED + 1),
        'by_company': company_means,
    }


def shared_stage_differences(key: list[dict], loaded: list[dict], first: str, second: str) -> dict[str, list[float]]:
    """Secondary analysis (DECISIONS, 21 November): each pair compared only on the dimensions both runs were scored on,
    per judge, then averaged over the judges (Stage 1's reached-only comparison); by company."""
    cells: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    for row in key:
        if row['arm'] in (first, second):
            cells[(row['case'], row['attempt'])][row['arm']] = row['packet_id']
    by_company: dict[str, list[float]] = defaultdict(list)
    for (case, _), arms in cells.items():
        if first not in arms or second not in arms:
            continue
        per_judge = []
        for predictions in loaded:
            a, b = predictions.get(arms[first]), predictions.get(arms[second])
            if not a or not b or not a['judgments'] or not b['judgments']:
                break
            da, db = (scored(p['judgments']) for p in (a, b))
            common = set(da) & set(db)
            if not common:
                break
            per_judge.append(statistics.mean(da[n] - db[n] for n in common))
        if len(per_judge) == len(loaded):
            by_company[case.split('-')[0]].append(statistics.mean(per_judge))
    return by_company


def scored(judgments: list[dict]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for judgment in judgments:
        for name, dimension in judgment['dimensions'].items():
            if dimension['status'] == REACHED:
                values[name].append(dimension['score'])
    return {name: statistics.mean(v) for name, v in values.items()}


def agreement(a: dict[int, float], b: dict[int, float]) -> dict:
    both = sorted(set(a) & set(b))
    return {
        'runs_scored_by_both': len(both),
        'spearman': float(spearmanr([a[i] for i in both], [b[i] for i in both]).statistic),
        'mean_absolute_difference': statistics.mean(abs(a[i] - b[i]) for i in both),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--judge', action='append', required=True, help='name=predictions.jsonl, exactly two')
    parser.add_argument('--compare', action='append', required=True, help='first,second (first minus second)')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    key = [json.loads(line) for line in args.key.read_text().splitlines() if line.strip()]
    judges = dict(spec.split('=', 1) for spec in args.judge)
    if len(judges) != 2:
        parser.error('the registered reading uses exactly two judges')
    per_judge = {name: run_scores(key, path) for name, path in judges.items()}
    (name_a, (scores_a, missing_a)), (name_b, (scores_b, missing_b)) = per_judge.items()
    both = set(scores_a) & set(scores_b)
    primary = {i: (scores_a[i] + scores_b[i]) / 2 for i in both}
    result: dict = {
        'runs': len(key),
        'missing': {name: [key[i]['packet_id'] for i in m] for name, (_, m) in per_judge.items()},
        'left_out_of_primary': len(key) - len(both),
        'agreement': agreement(scores_a, scores_b),
        'comparisons': [],
    }
    for spec in args.compare:
        first, second = spec.split(',')
        entry = {'primary_mean_of_judges': compare(key, primary, first, second)}
        for name, (scores, _) in per_judge.items():
            entry[name] = compare(key, scores, first, second)
        shared = shared_stage_differences(key, [load(path) for path in judges.values()], first, second)
        entry['secondary_shared_stages'] = {
            'pairs': sum(map(len, shared.values())),
            'mean_of_company_means': statistics.mean(statistics.mean(v) for v in shared.values()),
            'company_t_interval': company_t(shared),
            'company_bootstrap_interval': percentile_bootstrap(shared, SEED + 2),
        }
        signs = {name: entry[name]['mean_of_company_means'] > 0 for name in judges}
        entry['judges_disagree_in_sign'] = len(set(signs.values())) > 1
        result['comparisons'].append(entry)
    args.out.write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
