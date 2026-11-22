"""Recompute every development comparison the paper reports from the blind judge key and the judge's predictions, and
check that each appears in the paper as printed (difference and 95% interval, two decimals). One command, no GPU:
a reader with the published key and predictions can confirm every number in Section 4 without rerunning a model.

Usage: uv run python scripts/paper/check_numbers.py --key KEY.jsonl --predictions PRED.jsonl [--paper paper.tex]
Exit status 1 if any comparison is missing from the paper or differs from it.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from aemon.evaluation.judging.report import report

JUDGE = 'codexsol170'
PAPER = Path('docs/stage2/latex/paper.tex')


@dataclass(frozen=True)
class Claim:
    what: str
    first: str
    second: str


CLAIMS = (
    Claim('fine-tuning, seed 7 (A against the prompted 8B, same scaffold)', 'ayaA7_guards', 'ayaP_compact_guards'),
    Claim('fine-tuning, seed 11', 'ayaA11_guards', 'ayaP_compact_guards'),
    Claim('fine-tuning, seed 13', 'ayaA13_guards', 'ayaP_compact_guards'),
    Claim('A against the Stage 1 system, seed 7', 'ayaA7_guards', 'final_system'),
    Claim('recovery rows, seed 7 (B minus A)', 'ayaB7_guards', 'ayaA7_guards'),
    Claim('recovery rows, seed 11', 'ayaB11_guards', 'ayaA11_guards'),
    Claim('recovery rows, seed 13', 'ayaB13_guards', 'ayaA13_guards'),
    Claim('no correction rows, against A', 'ayaNC7_guards', 'ayaA7_guards'),
    Claim('no correction rows, against the prompted 8B', 'ayaNC7_guards', 'ayaP_compact_guards'),
    Claim('composition, against A', 'ayaC7_guards', 'ayaA7_guards'),
    Claim('no guards, against A', 'ayaA7_none', 'ayaA7_guards'),
    Claim('adapter off in the late stages, against A', 'ayaA7_routed', 'ayaA7_guards'),
    Claim('no quote menu, against A', 'ayaA7_minus_quote', 'ayaA7_guards'),
    Claim('refuse repeats instead of resampling, against A', 'ayaA7_minus_repeats', 'ayaA7_guards'),
    Claim('staged prompt, against A', 'ayaA7_staged_prompt', 'ayaA7_guards'),
    Claim('composition, seed 11', 'ayaC11_guards', 'ayaA11_guards'),
    Claim('composition, seed 13', 'ayaC13_guards', 'ayaA13_guards'),
    Claim('recovery round, seed 7', 'ayaR7_guards', 'ayaA7_guards'),
    Claim('recovery round, seed 11', 'ayaR11_guards', 'ayaA11_guards'),
    Claim('recovery round, seed 13', 'ayaR13_guards', 'ayaA13_guards'),
)


def printed_triples(tex: str) -> set[tuple[float, float, float]]:
    """Every 'x [y, z]' in the paper, as numbers: signs written as $-0.20$, +0.73 or 0.69 all read the same."""
    plain = tex.replace('$', '').replace('−', '-')
    number = r'([+-]?\d+\.\d+)'
    pattern = rf'{number}\s*\[\s*{number}\s*,\s*{number}\s*\]'
    return {tuple(round(float(g), 2) for g in m.groups()) for m in re.finditer(pattern, plain)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', required=True)
    parser.add_argument('--predictions', required=True)
    parser.add_argument('--paper', type=Path, default=PAPER)
    args = parser.parse_args()
    printed = printed_triples(args.paper.read_text())
    failures = 0
    for claim in CLAIMS:
        result = report(args.key, {JUDGE: args.predictions}, (claim.first, claim.second))
        mean, low, high = result['judges'][JUDGE]['difference']['mean_and_95_interval']
        triple = (round(mean, 2), round(low, 2), round(high, 2))
        found = triple in printed or (0.0, *triple[1:]) in printed and triple[0] == 0.0
        failures += not found
        status = 'in paper' if found else 'NOT IN PAPER'
        print(f'{status:13s} {mean:+.2f} [{low:+.2f}, {high:+.2f}]  {claim.what}')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
