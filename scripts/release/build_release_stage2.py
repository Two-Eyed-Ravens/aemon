"""Build the Stage 2 Hugging Face release (DECISIONS, 22 November: public now, test set 3 only after its run).

Model folder: A's seed-7 adapter (the GGUF that was served, and the PEFT files it was converted from) with a card.
Dataset folder: every Stage 2 development report, blind packet, judgment and answer key, the ablation and condition
tables, the retention check, the decision-model files, both hand checks with their keys, and the rows added by the
recovery round and the quantity condition, and, after its run, test set 3 (frozen cases and dossiers, the three
arms' reports, blind packets, key, both judges' predictions and the analysis). Personal and cluster identifiers are
replaced as in build_public_repo.py; MANIFEST.json lists each published file with its source and the sha256 of both.

Usage: uv run python scripts/release/build_release_stage2.py --adapter DIR --quantity-rows FILE --out DIR
  --adapter: a local copy of runs/base_aya-expanse-8b (adapter.gguf and adapter/); omit it to build the dataset only
"""

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KEYS = Path.home() / 'lexsi-backup' / 'judge_keys'
SCRUB = {
    'CLUSTER_ACCOUNT': 'CLUSTER_ACCOUNT',
    'CLUSTER_ACCOUNT_2': 'CLUSTER_ACCOUNT_2',
    'CLUSTER_HOST': 'CLUSTER_HOST',
    '/home/USER': '/home/USER',
    '/home/USER': '/home/USER',
}
TEXT = {'.json', '.jsonl', '.md', '.txt', '.log', '.jinja', '.html'}
CARDS = REPO / 'docs' / 'stage2' / 'hf'


@dataclass(frozen=True)
class Item:
    source: Path
    published: str


def dataset_items(quantity_rows: Path) -> list[Item]:
    screen = REPO / 'experiments' / 'screen'
    items = [Item(p, f'screens/{p.name}') for p in sorted(screen.glob('*.json'))]
    judging = screen / 'judging'
    items += [Item(p, f'judging/{p.name}') for p in sorted(judging.glob('*stage2*'))]
    items += [Item(p, f'judging/recomputed/{p.name}') for p in sorted((judging / 'recomputed').glob('*.json'))]
    items += [Item(p, f'judging/keys/{p.name}') for p in sorted(KEYS.glob('stage2*_key.jsonl'))]
    for folder in ('judge_check', 'retention', 'decider', 'recovery_round1'):
        base = REPO / 'experiments' / folder
        items += [Item(p, f'{folder}/{p.relative_to(base)}') for p in sorted(base.rglob('*')) if p.is_file()]
    items += [Item(KEYS / name, f'judge_check/keys/{name}') for name in ('hand_check_key.json', 'hand_pairs_key.json')]
    items.append(Item(quantity_rows, 'quantity/quantity_rows.jsonl'))
    return [i for i in items if 'test3' not in i.published and 'heldout3' not in i.published] + test3_items()


def test3_items() -> list[Item]:
    run = REPO / 'experiments' / 'test3'
    names = (
        'A.json',
        'prompted.json',
        'stage1.json',
        'packets.jsonl',
        'test3_key.jsonl',
        'report.json',
        'codexsol170_run.log',
        'claudecode_run.log',
        'claudecode_rejudge.log',
        'validation_on_stage1_test2.json',
    )
    items = [Item(run / name, f'test3/{name}') for name in names]
    items += [Item(p, f'test3/judging/{p.name}') for p in sorted((run / 'judging').glob('*.jsonl'))]
    haiku = run / 'haiku'
    names = (
        'haiku_merged.json',
        'haiku_merged.auditkit.json',
        'packets.jsonl',
        'test3_haiku_key.jsonl',
        'report.json',
        'judge.sh',
        'report_without_refusals.json',
        'test3_haiku_key_without_refusals.jsonl',
        'rerun.sh',
        'analyze.sh',
    )
    items += [Item(haiku / name, f'test3/haiku/{name}') for name in names]
    items += [Item(p, f'test3/haiku/judging/{p.name}') for p in sorted((haiku / 'judging').glob('*.jsonl'))]
    dossier = REPO / 'data' / 'dossier'
    items.append(Item(dossier / 'cases_heldout3.json', 'test3/frozen/cases_heldout3.json'))
    items.append(Item(REPO / 'docs' / 'test3_freeze.json', 'test3/frozen/test3_freeze.json'))
    raw = dossier / 'raw' / 'heldout3'
    items += [Item(p, f'test3/frozen/dossiers/{p.relative_to(raw)}') for p in sorted(raw.rglob('*')) if p.is_file()]
    return items


def model_items(adapter: Path) -> list[Item]:
    items = [Item(adapter / 'adapter.gguf', 'aemon-8b-adapter.gguf')]
    peft = adapter / 'adapter'
    keep = ('adapter_config.json', 'adapter_model.safetensors', 'chat_template.jinja', 'tokenizer.json', 'tokenizer_config.json')
    return items + [Item(peft / name, f'peft/{name}') for name in keep]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def publish(items: list[Item], out: Path) -> list[dict]:
    manifest = []
    for item in items:
        target = out / item.published
        target.parent.mkdir(parents=True, exist_ok=True)
        original = item.source.read_bytes()
        published = original
        counts = {}
        if item.source.suffix in TEXT:
            text = original.decode('utf-8', errors='surrogateescape')
            for old, placeholder in SCRUB.items():
                if old in text:
                    counts[placeholder] = text.count(old)
                    text = text.replace(old, placeholder)
            published = text.encode('utf-8', errors='surrogateescape')
        target.write_bytes(published)
        entry = {
            'file': item.published,
            'from': str(item.source).replace('/home/USER', '/home/USER'),
            'sha256_original': sha(original),
            'sha256_published': sha(published),
        }
        if counts:
            entry['replaced'] = counts
        manifest.append(entry)
    return manifest


def leftover_identifiers(out: Path) -> int:
    found = 0
    for path in out.rglob('*'):
        if path.is_file() and path.suffix in TEXT:
            text = path.read_text(errors='ignore')
            found += sum(text.count(k) for k in SCRUB)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--adapter', type=Path)
    parser.add_argument('--quantity-rows', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        shutil.rmtree(args.out)
    builds = [('dataset', dataset_items(args.quantity_rows), 'DATASET_CARD.md')]
    if args.adapter:
        builds.append(('model', model_items(args.adapter), 'MODEL_CARD.md'))
    for name, items, card in builds:
        folder = args.out / name
        manifest = publish(items, folder)
        shutil.copy(CARDS / card, folder / 'README.md')
        (folder / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1) + '\n')
        size = sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
        print(json.dumps({'folder': name, 'files': len(manifest), 'megabytes': round(size / 1e6, 1), 'identifiers_left': leftover_identifiers(folder)}))


if __name__ == '__main__':
    main()
