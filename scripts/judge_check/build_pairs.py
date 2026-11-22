"""Second blind hand check (DECISIONS, 20 November): does a human see the main gap the judge sees? Ten matched pairs
(same case and attempt) of A at seed 7 and the prompted 8B on the same scaffold, seeded and spread over the six
companies, shown as 20 shuffled packets labelled P01..P20, so neither the arm nor the pairing is visible. Scored on
problem framing and evidence judgement, which the prompted model does reach. The key stays outside the repository.

Usage: python scripts/judge_check/build_pairs.py --out experiments/judge_check --key ~/lexsi-backup/judge_keys/hand_pairs_key.json
"""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from build_sample import JUDGING, TEMPLATE

KEY = Path.home() / 'lexsi-backup/judge_keys/stage2k_all_key.jsonl'
PREDICTIONS = JUDGING / 'codexsol170_predictions_stage2k_all.jsonl'
PACKET_FILES = ('packets_stage2_A7_guards.jsonl', 'packets_stage2_Pc_guards.jsonl')
ARMS = ('ayaA7_guards', 'ayaP_compact_guards')
DIMENSIONS = ('problem_framing', 'evidence_judgement')
PAIRS = 10
SEED = 21


def eligible_pairs() -> dict[tuple[str, int], dict[str, str]]:
    judged = {}
    for line in PREDICTIONS.read_text().splitlines():
        row = json.loads(line)
        judged[row['packet_id']] = row['judgment']['dimensions']
    cells: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    for row in map(json.loads, KEY.read_text().splitlines()):
        dims = judged.get(row['packet_id'], {})
        if row['arm'] in ARMS and all(dims.get(d, {}).get('status') == 'scored' for d in DIMENSIONS):
            cells[(row['case'], row['attempt'])][row['arm']] = row['packet_id']
    return {cell: arms for cell, arms in cells.items() if len(arms) == len(ARMS)}


def sample(pairs: dict[tuple[str, int], dict[str, str]]) -> list[tuple[tuple[str, int], dict[str, str]]]:
    """Round-robin over companies in a seeded order, never reusing a packet."""
    rng = random.Random(SEED)
    by_company: dict[str, list] = defaultdict(list)
    for cell in sorted(pairs):
        by_company[cell[0].split('-')[0]].append(cell)
    for cells in by_company.values():
        rng.shuffle(cells)
    companies = sorted(by_company)
    rng.shuffle(companies)
    chosen, used = [], set()
    while len(chosen) < PAIRS and any(by_company.values()):
        for company in companies:
            while by_company[company] and len(chosen) < PAIRS:
                cell = by_company[company].pop()
                ids = set(pairs[cell].values())
                if not ids & used:
                    chosen.append((cell, pairs[cell]))
                    used |= ids
                    break
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--key', type=Path, required=True)
    args = parser.parse_args()
    packets = {}
    for name in PACKET_FILES:
        for line in (JUDGING / name).read_text().splitlines():
            packet = json.loads(line)
            packets[packet['packet_id']] = packet
    chosen = sample(eligible_pairs())
    entries = [(cell, arm, pid) for cell, arms in chosen for arm, pid in arms.items()]
    random.Random(SEED + 1).shuffle(entries)
    labelled, key = [], {}
    for i, (cell, arm, pid) in enumerate(entries):
        label = f'P{i + 1:02d}'
        labelled.append(dict(packets[pid], packet_id=label))
        key[label] = {'packet_id': pid, 'arm': arm, 'case': cell[0], 'attempt': cell[1]}
    page = TEMPLATE.read_text().replace('__PACKETS__', json.dumps(labelled)).replace('__DIMENSIONS__', json.dumps(list(DIMENSIONS)))
    page = page.replace('__STORE__', json.dumps('judge-hand-pairs-v1'))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'hand_pairs.html').write_text(page)
    args.key.write_text(json.dumps(key, indent=1))
    companies = sorted({cell[0].split('-')[0] for cell, _ in chosen})
    print(json.dumps({'pairs': len(chosen), 'packets': len(labelled), 'companies': companies, 'page': str(args.out / 'hand_pairs.html')}))


if __name__ == '__main__':
    main()
