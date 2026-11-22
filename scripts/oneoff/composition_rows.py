"""The composition condition of the training-data experiment (DECISIONS 19 November): the same teacher rows, resampled so
the decision skills the student is weakest at get a larger share of the supervised tokens, at the reference's total
token budget. No new teacher output is used.

Skill groups by stage: procedure (brief, frame, evidence, challenge, challenge_reading, new_evidence), theories,
assessment, test (propose or decline), revision (update), recommendation (position, conclude). Each group's target
share of target characters is proportional to its current share to the power 0.5 (temperature sampling, which lifts
small groups without making them dominate), and rows are drawn with replacement within each group, seeded. Rows of
the validation companies are copied unchanged, so the held-out loss is computed on exactly the reference's rows.

Usage: python scripts/oneoff/composition_rows.py rows/final.jsonl rows/composition_s7.jsonl
"""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from aemon.common.constants.pipeline import VALIDATION_COMPANIES

GROUPS = {
    'brief': 'procedure',
    'frame': 'procedure',
    'evidence': 'procedure',
    'challenge': 'procedure',
    'challenge_reading': 'procedure',
    'new_evidence': 'procedure',
    'theories': 'theories',
    'assessment': 'assessment',
    'test': 'test',
    'update': 'revision',
    'position': 'recommendation',
    'conclude': 'recommendation',
}
TEMPERATURE = 0.5
SEED = 7


def size(row: dict) -> int:
    return len(row['messages'][row['target_index']]['content'])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('rows', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('rows are never overwritten')
    with args.rows.open() as handle:
        rows = [json.loads(line) for line in handle]
    held = [r for r in rows if r['case'].startswith(VALIDATION_COMPANIES)]
    train = [r for r in rows if not r['case'].startswith(VALIDATION_COMPANIES)]
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in train:
        by_group[GROUPS[row['stage']]].append(row)
    current = {g: sum(size(r) for r in rs) for g, rs in by_group.items()}
    budget = sum(current.values())
    weights = {g: t**TEMPERATURE for g, t in current.items()}
    target = {g: budget * w / sum(weights.values()) for g, w in weights.items()}
    rng = random.Random(SEED)
    made: list[dict] = []
    for group in sorted(by_group):
        pool, got = by_group[group], 0
        while got < target[group]:
            row = rng.choice(pool)
            made.append(row)
            got += size(row)
    rng.shuffle(made)
    with args.output.open('w') as handle:
        for row in made + held:
            handle.write(json.dumps(row) + '\n')
    report = {
        g: {
            'rows_before': len(by_group[g]),
            'rows_after': sum(GROUPS[r['stage']] == g for r in made),
            'share_before': round(current[g] / budget, 3),
            'share_after': round(target[g] / budget, 3),
        }
        for g in sorted(by_group)
    }
    print(json.dumps({'budget_chars': budget, 'made_chars': sum(size(r) for r in made), 'validation_rows_kept': len(held), 'groups': report}, indent=1))


if __name__ == '__main__':
    main()
