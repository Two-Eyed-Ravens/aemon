"""Does the hand scorer see the gap the judge sees (DECISIONS, 20 November)? For each matched pair, the difference
A minus prompted per dimension, by hand and by the judge: the mean gap for each rater, how many pairs each rater puts
A ahead, level or behind, and how often the two raters' signs agree.

Usage: python scripts/judge_check/pair_agreement.py --scores hand_pairs_scores.json --key ~/lexsi-backup/judge_keys/hand_pairs_key.json
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

PREDICTIONS = Path('experiments/screen/judging/codexsol170_predictions_stage2k_all.jsonl')
FIRST, SECOND = 'ayaA7_guards', 'ayaP_compact_guards'


def sign(x: float) -> int:
    return (x > 0) - (x < 0)


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
    pairs: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    for label, entry in key.items():
        pairs[(entry['case'], entry['attempt'])][entry['arm']] = label
    result = {}
    for dimension in exported['dimensions']:
        hand_gaps, judge_gaps = [], []
        for labels in pairs.values():
            hand = [exported['scores'].get(labels[arm], {}).get(dimension) for arm in (FIRST, SECOND)]
            if any(h is None for h in hand):
                continue
            judge = [judged[key[labels[arm]]['packet_id']][dimension]['score'] for arm in (FIRST, SECOND)]
            hand_gaps.append(int(hand[0]) - int(hand[1]))
            judge_gaps.append(judge[0] - judge[1])
        n = len(hand_gaps)
        result[dimension] = {
            'pairs': n,
            'hand_mean_gap': sum(hand_gaps) / n,
            'judge_mean_gap': sum(judge_gaps) / n,
            'hand_a_ahead_level_behind': [sum(g > 0 for g in hand_gaps), sum(g == 0 for g in hand_gaps), sum(g < 0 for g in hand_gaps)],
            'judge_a_ahead_level_behind': [sum(g > 0 for g in judge_gaps), sum(g == 0 for g in judge_gaps), sum(g < 0 for g in judge_gaps)],
            'sign_agreement': sum(sign(h) == sign(j) for h, j in zip(hand_gaps, judge_gaps, strict=True)) / n,
        }
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
