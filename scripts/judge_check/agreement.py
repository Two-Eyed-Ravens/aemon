"""Agreement between the blind hand scores and the judge (DECISIONS, 20 November): per dimension, exact agreement,
agreement within one point, Spearman correlation, and the mean difference in level (judge minus hand), overall and by
arm. Reads the exported page scores, the private key and the judge's saved predictions.

Usage: python scripts/judge_check/agreement.py --scores hand_check_scores.json --key ~/lexsi-backup/judge_keys/hand_check_key.json
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

PREDICTIONS = Path('experiments/screen/judging/codexsol170_predictions_stage2i_all.jsonl')


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2
        i = j + 1
    return out


def spearman(a: list[float], b: list[float]) -> float | None:
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=True))
    sa = sum((x - ma) ** 2 for x in ra) ** 0.5
    sb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (sa * sb) if sa and sb else None


def summary(pairs: list[tuple[int, int]]) -> dict:
    hand, judge = [p[0] for p in pairs], [p[1] for p in pairs]
    return {
        'n': len(pairs),
        'exact': sum(h == j for h, j in pairs) / len(pairs),
        'within_one': sum(abs(h - j) <= 1 for h, j in pairs) / len(pairs),
        'spearman': spearman(hand, judge),
        'mean_hand': sum(hand) / len(hand),
        'mean_judge': sum(judge) / len(judge),
        'judge_minus_hand': (sum(judge) - sum(hand)) / len(pairs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--scores', type=Path, required=True)
    parser.add_argument('--key', type=Path, required=True)
    args = parser.parse_args()
    exported = json.loads(args.scores.read_text())
    key = json.loads(args.key.read_text())
    judged = {}
    for line in PREDICTIONS.read_text().splitlines():
        row = json.loads(line)
        judged[row['packet_id']] = row['judgment']['dimensions']
    result: dict = {}
    for dimension in exported['dimensions']:
        pairs, by_arm = [], defaultdict(list)
        for label, entry in exported['scores'].items():
            hand = entry.get(dimension)
            judge = judged[key[label]['packet_id']].get(dimension, {})
            if hand is None or judge.get('status') != 'scored':
                continue
            pair = (int(hand), int(judge['score']))
            pairs.append(pair)
            by_arm[key[label]['arm']].append(pair)
        result[dimension] = {'all': summary(pairs), 'by_arm': {arm: summary(p) for arm, p in sorted(by_arm.items())}}
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
