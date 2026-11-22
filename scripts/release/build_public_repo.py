"""Build the public GitHub snapshot of this repository: no history, no third-party papers, and personal or internal
identifiers replaced by placeholders. The dossier is published as it is (Hatem, 2026-11-11: "keep them as they are and
publish them"), so public runs read the same excerpts as the evaluated ones. The earlier cut to one short quote per
excerpt is removed from this build.

Usage: python scripts/release/build_public_repo.py --out DIR
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parents[2]
DROP = (
    'papers/',
    'sources/',
    'docs/PUBLIC_README.md',
    'SUMMARY.md',
    'TODO.md',
    # working notes for the people and agents building it, and an older draft the README supersedes
    'docs/AGENT_BRIEF.md',
    'docs/SCHEDULE.md',
    'docs/ARTICLE_DRAFT.md',
    # Stage 2 working notes and the superseded Markdown draft of the paper (the LaTeX source is the paper)
    'docs/stage2/MORNING_REPORT_',
    'docs/stage2/PAPER_DRAFT.md',
    'docs/stage2/PAPER_OUTLINE.md',
    'docs/stage2/RELEASE_CHECKLIST.md',
    # the rewording table itself, and notes that are only about AI assistants' work (handovers, their advisory
    # reviews, a review of an assistant's code, how an assistant fetched a source)
    'scripts/release/public_rewording.json',
    'docs/archive/',
    'docs/reviews/codex_handover.md',
    'docs/briefs/',
    'docs/reviews/beyond-black-boxes-source-check.md',
    'reviews/reproduction/',
    'reviews/v2_round2/advisory_',
    'reviews/v2_examples/advisory_review_gemini.txt',
    # product-phase plans and labelling sheets (with their key) stay private until Hatem says otherwise
    'docs/PRODUCT_PLAN.md',
    'docs/SIMULATION_DESIGN.md',
    'docs/RIGHTS_AUDIT.md',
    'reports/labelling/',
)
# the source papers and their extracted text are the publishers', not ours; internal working notes stay private too
# Personal and internal identifiers, replaced by placeholders in the public copy (named in the README)
SCRUB = {
    'CLUSTER_ACCOUNT': 'CLUSTER_ACCOUNT',
    'CLUSTER_ACCOUNT_2': 'CLUSTER_ACCOUNT_2',
    'CLUSTER_HOST': 'CLUSTER_HOST',
    '/home/USER': '/home/USER',
    '/home/USER': '/home/USER',
}
# Notes that an AI assistant did some of the work are reworded to what was done, in the public copy only (Hatem,
# 21 November); the table lives in a file the public copy leaves out, since it holds the phrases it removes. The judges
# keep their names: they are the instruments. Each pair must match exactly once.
PUBLIC_EDITS = json.loads((REPO / 'scripts/release/public_rewording.json').read_text())
REWORD = PUBLIC_EDITS['reword']
CUT_SECTIONS = PUBLIC_EDITS['cut_sections']


def cut_section(text: str, heading: str, path: str) -> str:
    """Remove the section under `heading` up to the next heading of the same or a higher level."""
    lines = text.split('\n')
    starts = [i for i, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        raise SystemExit(f'section not found exactly once in {path}: {heading[:60]}')
    level = len(heading) - len(heading.lstrip('#'))
    start = starts[0]
    end = start + 1
    while end < len(lines):
        marks = len(lines[end]) - len(lines[end].lstrip('#'))
        if 0 < marks <= level and lines[end][marks : marks + 1] == ' ':
            break
        end += 1
    return '\n'.join(lines[:start] + lines[end:])


TEXT = {
    '.sha256',
    '.sha',
    '.jinja',
    '.py',
    '.md',
    '.json',
    '.jsonl',
    '.txt',
    '.ts',
    '.tsx',
    '.js',
    '.css',
    '.html',
    '.sh',
    '.sbatch',
    '.toml',
    '.cfg',
    '.yml',
    '.yaml',
    '.csv',
    '.log',
    '.out',
    '.err',
    '.tex',
    '.bib',
    '.R',
}


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument('--out', required=True)
    args = a.parse_args()
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    files = subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()
    changed = dropped = 0
    for f in files:
        if f.startswith(DROP):
            dropped += 1
            continue
        src, dst = REPO / f, out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in TEXT:
            text = src.read_text(errors='surrogateescape')
            new = text
            for old, placeholder in SCRUB.items():
                new = new.replace(old, placeholder)
            for before, after in REWORD.get(f, []):
                if new.count(before) != 1:
                    raise SystemExit(f'reword not found exactly once in {f}: {before[:60]}')
                new = new.replace(before, after)
            for heading in CUT_SECTIONS.get(f, []):
                new = cut_section(new, heading, f)
            changed += new != text
            dst.write_text(new, errors='surrogateescape')
        else:
            shutil.copy2(src, dst)
    # The public README is its own document: results and how to run them, without the internal working notes
    (out / 'README.md').write_text((REPO / 'docs/PUBLIC_README.md').read_text())
    text_files = [p for p in out.rglob('*') if p.is_file()]  # every file, so a type missing from TEXT is caught
    unscrubbed = sum(p.read_text(errors='ignore').count(k) for p in text_files for k in SCRUB)
    print(json.dumps({'files': len(files) - dropped, 'dropped': dropped, 'redacted_files': changed, 'excerpts': 'as they are', 'identifiers_left': unscrubbed}))


if __name__ == '__main__':
    main()
