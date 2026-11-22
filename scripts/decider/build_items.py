"""Items for the trained decision head (DECISIONS, 20 November, registered and amended before any result):
evidence-kind questions from the training companies only, split by company scope into training and calibration.

Two sources, both labelled with the dossier's annotated kind of the record:
1. the record's excerpt, cut at a sentence end near 400 characters (the whole record, so its label fits);
2. the quotes Command A+ chose in its own assess_evidence calls in the teacher rows (rows/final.jsonl), the same kind
   of agent-chosen quote the frozen test items are.
Records sharing an eight-word run with any frozen test quote are left out. The offline file is the 161 frozen-test
items plus the calibration items, so one pass of scripts/bench/decision_logits.py scores both.

Usage: python scripts/decider/build_items.py --out experiments/decider
"""

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from aemon.agent.decision import KINDS
from aemon.common.constants.pipeline import VALIDATION_COMPANIES

DOSSIER = Path('data/dossier')
CASE_FILES = ('cases.json', 'cases_heldout.json', 'cases_heldout2.json', 'cases_heldout3.json')
FROZEN_ITEMS = Path('reports/decision_logits/decision_items.jsonl')
TEACHER_ROWS = Path('rows/final.jsonl')
CALIBRATION_SHARE = 0.15
SEED = 7
EXCERPT_CHARS = 400


@dataclass(frozen=True)
class Item:
    id: str
    task: str
    split: str
    source: str
    record: str
    quote: str
    title: str
    origin: str
    gold: str
    agent: dict[str, list[str]]


def case_scopes(name: str) -> set[str]:
    cases = json.loads((DOSSIER / name).read_text())
    listed = cases if isinstance(cases, list) else cases.get('cases', cases)
    rows = listed if isinstance(listed, list) else list(listed.values())
    return {case['scope'] for case in rows}


def training_scopes() -> list[str]:
    development = case_scopes(CASE_FILES[0])
    held_out = set().union(*(case_scopes(name) for name in CASE_FILES[1:]))
    validation = {scope for scope in development if scope.split('-')[0] in VALIDATION_COMPANIES}
    return sorted(development - held_out - validation)


def shingles(text: str, width: int = 8) -> set[str]:
    words = text.lower().split()
    return {' '.join(words[k : k + width]) for k in range(max(1, len(words) - width + 1))}


def excerpt_quote(excerpt: str) -> str:
    text = ' '.join(excerpt.split())
    head = ''
    for sentence in (s for s in re.split(r'(?<=[.!?])\s+', text) if s):
        if head and len(head) + len(sentence) > EXCERPT_CHARS:
            break
        head = f'{head} {sentence}'.strip()
    return head or text[:EXCERPT_CHARS]


def teacher_quotes() -> dict[str, set[str]]:
    """The quotes Command A+ chose per record in its accepted assess_evidence calls."""
    found: dict[str, set[str]] = {}
    for line in TEACHER_ROWS.read_text().splitlines():
        row = json.loads(line)
        try:
            call = json.loads(row['messages'][row['target_index']]['content'])
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(call, dict) and call.get('name') == 'assess_evidence':
            arguments = call['arguments']
            found.setdefault(arguments['evidence_id'], set()).add(' '.join(arguments['quote'].split()))
    return found


def item(record: dict, split: str, source: str, quote: str, n: int) -> Item:
    origin = 'company_claim' if record['type'] == 'company_claim' else 'verified_observation'
    return Item(f'{split}-{source}-{record["id"]}-{n}', 'evidence_kind', split, source, record['id'], quote, record['title'], origin, record['kind'], {})


def items_for(records: list[dict], split: str, chosen: dict[str, set[str]]) -> list[Item]:
    built = []
    for record in records:
        built.append(item(record, split, 'excerpt', excerpt_quote(record['excerpt']), 0))
        for n, quote in enumerate(sorted(chosen.get(record['id'], ()))):
            built.append(item(record, split, 'teacher', quote, n))
    return built


def write(path: Path, rows: list[dict]) -> None:
    with path.open('w') as handle:
        for row in rows:
            handle.write(json.dumps(row) + '\n')


def summary(scopes: list[str], calibration: set[str], records: list[dict], left_out: list[str], train: list[Item], held: list[Item]) -> dict:
    ids = sorted(r['id'] for r in records)
    return {
        'training_scopes': len(scopes),
        'calibration_scopes': sorted(calibration),
        'records': len(ids),
        'records_sha256': hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
        'records_left_out_for_overlap': left_out,
        'train_items': len(train),
        'train_by_source': dict(Counter(i.source for i in train)),
        'train_by_kind': dict(Counter(i.gold for i in train)),
        'train_third_party_by_kind': dict(Counter(i.gold for i in train if i.origin != 'company_claim')),
        'calibration_items': len(held),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    scopes = training_scopes()
    calibration = set(random.Random(SEED).sample(scopes, round(len(scopes) * CALIBRATION_SHARE)))
    frozen = [json.loads(line) for line in FROZEN_ITEMS.read_text().splitlines()]
    frozen_shingles = set().union(*(shingles(i['quote']) for i in frozen if i['task'] == 'evidence_kind'))
    candidates = [r for r in json.loads((DOSSIER / 'evidence.json').read_text())['records'] if r['kind'] in KINDS and r['scope'] in scopes]
    left_out = sorted(r['id'] for r in candidates if shingles(r['excerpt']) & frozen_shingles)
    records = [r for r in candidates if r['id'] not in left_out]
    chosen = teacher_quotes()
    train = items_for([r for r in records if r['scope'] not in calibration], 'train', chosen)
    held = items_for([r for r in records if r['scope'] in calibration], 'calibration', chosen)
    args.out.mkdir(parents=True, exist_ok=True)
    write(args.out / 'train_items.jsonl', [asdict(i) for i in train])
    write(args.out / 'calibration_items.jsonl', [asdict(i) for i in held])
    write(args.out / 'offline_items.jsonl', frozen + [asdict(i) for i in held])
    result = summary(scopes, calibration, records, left_out, train, held)
    (args.out / 'items_summary.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
