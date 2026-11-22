"""Blind hand check of the judge (DECISIONS, 20 November): a seeded sample of development packets, stratified over four
arms, shown under neutral labels H01..H30 in a self-contained page for scoring two rubric dimensions (evidence
judgement, recommendation). The key mapping labels to packets and arms is written outside the repository, so the
scorer stays blind until the scores are exported.

Usage: python scripts/judge_check/build_sample.py --out experiments/judge_check --key ~/lexsi-backup/judge_keys/hand_check_key.json
"""

import argparse
import json
import random
from pathlib import Path

JUDGING = Path('experiments/screen/judging')
KEY = Path.home() / 'lexsi-backup/judge_keys/stage2i_all_key.jsonl'
PREDICTIONS = JUDGING / 'codexsol170_predictions_stage2i_all.jsonl'
PACKET_FILES = ('packets_stage2_A7_guards.jsonl', 'packets_stage2_B7_guards.jsonl', 'packets_stage2_B11_guards.jsonl', 'packets.jsonl')
ARMS = {'ayaA7_guards': 8, 'ayaB7_guards': 8, 'ayaB11_guards': 7, 'final_system': 7}
DIMENSIONS = ('evidence_judgement', 'recommendation')
SEED = 20
TEMPLATE = Path(__file__).with_name('page_template.html')


def judged_scores() -> dict[str, dict[str, int]]:
    scores: dict[str, dict[str, int]] = {}
    for line in PREDICTIONS.read_text().splitlines():
        row = json.loads(line)
        dims = row['judgment']['dimensions']
        if all(dims.get(d, {}).get('status') == 'scored' for d in DIMENSIONS):
            scores[row['packet_id']] = {d: dims[d]['score'] for d in DIMENSIONS}
    return scores


def packets_by_id() -> dict[str, dict]:
    found = {}
    for name in PACKET_FILES:
        path = JUDGING / name
        if path.exists():
            for line in path.read_text().splitlines():
                packet = json.loads(line)
                found[packet['packet_id']] = packet
    return found


def sample(arm_of: dict[str, str], eligible: set[str]) -> list[str]:
    rng = random.Random(SEED)
    chosen = []
    for arm, n in ARMS.items():
        pool = sorted(p for p, a in arm_of.items() if a == arm and p in eligible)
        chosen += rng.sample(pool, n)
    rng.shuffle(chosen)
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--key', type=Path, required=True)
    args = parser.parse_args()
    arm_of = {row['packet_id']: row['arm'] for row in map(json.loads, KEY.read_text().splitlines())}
    packets = packets_by_id()
    eligible = set(judged_scores()) & set(packets)
    chosen = sample(arm_of, eligible)
    labelled = [dict(packets[p], packet_id=f'H{i + 1:02d}') for i, p in enumerate(chosen)]
    key = {f'H{i + 1:02d}': {'packet_id': p, 'arm': arm_of[p]} for i, p in enumerate(chosen)}
    args.out.mkdir(parents=True, exist_ok=True)
    page = (
        TEMPLATE.read_text()
        .replace('__PACKETS__', json.dumps(labelled))
        .replace('__DIMENSIONS__', json.dumps(list(DIMENSIONS)))
        .replace('__STORE__', json.dumps('judge-hand-check-v1'))
    )
    (args.out / 'hand_check.html').write_text(page)
    args.key.parent.mkdir(parents=True, exist_ok=True)
    args.key.write_text(json.dumps(key, indent=1))
    print(json.dumps({'packets': len(labelled), 'by_arm': ARMS, 'page': str(args.out / 'hand_check.html'), 'key': str(args.key)}))


if __name__ == '__main__':
    main()
