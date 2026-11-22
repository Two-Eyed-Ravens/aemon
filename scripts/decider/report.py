"""Calibrate and compare the zero-shot base and the trained decision head (DECISIONS, 20 November, registered).

For each arm one temperature is fitted by log-loss on the calibration split (training companies never trained on),
then applied to the frozen evidence-kind items. Reports accuracy, expected calibration error, coverage and accuracy at
the fixed 0.9 threshold, for all items and for third-party sources alone (the only ones decide_kind acts on), the paired
accuracy difference with a bootstrap interval, and the registered go rule for an in-loop run.

Usage: python scripts/decider/report.py --logits decision_logits.json --out decider_report.json
"""

import argparse
import json
import math
import random
from pathlib import Path

from aemon.agent.decision import DEFAULT_THRESHOLD, KINDS

TEMPERATURES = [round(0.25 + 0.05 * k, 2) for k in range(196)]
GO_MARGIN = 0.05
BOOTSTRAP = 5000
SEED = 7


def tempered(probs: dict[str, float], temperature: float) -> dict[str, float]:
    if not probs:
        return {}
    weights = {k: math.exp(math.log(max(v, 1e-12)) / temperature) for k, v in probs.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}


def log_loss(rows: list[dict], temperature: float) -> float:
    total = 0.0
    for row in rows:
        probs = tempered(row['probs'], temperature)
        total -= math.log(max(probs.get(row['gold'], 0.0), 1e-12))
    return total / len(rows)


def fit_temperature(rows: list[dict]) -> float:
    return min(TEMPERATURES, key=lambda t: log_loss(rows, t))


def scored(rows: list[dict], temperature: float) -> list[dict]:
    out = []
    for row in rows:
        probs = tempered(row['probs'], temperature)
        complete = len(probs) == len(KINDS)
        best = max(probs, key=lambda k: probs[k]) if probs else None
        out.append({'id': row['id'], 'gold': row['gold'], 'pred': best, 'conf': probs.get(best, 0.0) if best else 0.0, 'complete': complete})
    return out


def ece(rows: list[dict], bins: int = 10) -> float:
    total = 0.0
    for b in range(bins):
        chosen = [r for r in rows if b / bins < r['conf'] <= (b + 1) / bins]
        if chosen:
            accuracy = sum(r['pred'] == r['gold'] for r in chosen) / len(chosen)
            confidence = sum(r['conf'] for r in chosen) / len(chosen)
            total += len(chosen) / len(rows) * abs(accuracy - confidence)
    return total


def metrics(rows: list[dict]) -> dict:
    acting = [r for r in rows if r['complete'] and r['conf'] >= DEFAULT_THRESHOLD]
    return {
        'n': len(rows),
        'accuracy': sum(r['pred'] == r['gold'] for r in rows) / len(rows),
        'ece': ece(rows),
        'missing_letter_rate': sum(not r['complete'] for r in rows) / len(rows),
        'coverage_at_threshold': len(acting) / len(rows),
        'accuracy_at_threshold': sum(r['pred'] == r['gold'] for r in acting) / len(acting) if acting else None,
        'accuracy_by_gold': {k: sum(r['pred'] == k for r in rows if r['gold'] == k) / g for k in KINDS if (g := sum(r['gold'] == k for r in rows))},
    }


def paired_interval(base: list[dict], head: list[dict], record: dict[str, str]) -> dict:
    """The paired accuracy difference, with a bootstrap over records (several quotes can come from one record)."""
    by_record: dict[str, list[int]] = {}
    for b, h in zip(base, head, strict=True):
        by_record.setdefault(record[b['id']], []).append((h['pred'] == h['gold']) - (b['pred'] == b['gold']))
    clusters = list(by_record.values())
    rng = random.Random(SEED)
    means = []
    for _ in range(BOOTSTRAP):
        drawn = [rng.choice(clusters) for _ in clusters]
        means.append(sum(map(sum, drawn)) / sum(map(len, drawn)))
    means.sort()
    diffs = [d for cluster in clusters for d in cluster]
    return {
        'mean_and_95_interval': [sum(diffs) / len(diffs), means[int(0.025 * BOOTSTRAP)], means[int(0.975 * BOOTSTRAP)]],
        'head_right_base_wrong': diffs.count(1),
        'base_right_head_wrong': diffs.count(-1),
        'records': len(clusters),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--logits', type=Path, required=True)
    parser.add_argument('--items', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    items = {str(item['id']): item for item in map(json.loads, args.items.read_text().splitlines())}
    rows = json.loads(args.logits.read_text())['rows']
    result: dict = {'arms': {}}
    frozen: dict[str, list[dict]] = {}
    for arm in ('base', 'decider'):
        kind_rows = [dict(r, id=str(r['id'])) for r in rows[arm] if r['task'] == 'evidence_kind']
        calibration = [r for r in kind_rows if r['id'].startswith('calibration-')]
        test = [r for r in kind_rows if not r['id'].startswith('calibration-')]
        temperature = fit_temperature(calibration)
        frozen[arm] = scored(test, temperature)
        third_party = [r for r in frozen[arm] if items[r['id']]['origin'] != 'company_claim']
        result['arms'][arm] = {
            'temperature': temperature,
            'calibration_uncalibrated': metrics(scored(calibration, 1.0)),
            'frozen_uncalibrated': metrics(scored(test, 1.0)),
            'frozen': metrics(frozen[arm]),
            'frozen_third_party': metrics(third_party),
        }
    base, head = result['arms']['base']['frozen'], result['arms']['decider']['frozen']
    record = {key: str(item.get('record', key)) for key, item in items.items()}
    difference = paired_interval(frozen['base'], frozen['decider'], record)
    result['accuracy_difference'] = difference
    # registered rule, amended before any result: also the record-level interval's lower bound above zero
    result['go'] = head['accuracy'] >= base['accuracy'] + GO_MARGIN and head['ece'] <= base['ece'] and difference['mean_and_95_interval'][1] > 0
    args.out.write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
