"""Update the development comparisons printed in the paper to the latest merged judgments. For each comparison
check_numbers.py knows, the value printed in the paper is found by recomputing it on each earlier merge (newest first)
until one matches a printed 'x [y, z]'; that printed occurrence is replaced by the value on the latest merge, keeping
its formatting ($-0.20$ or +0.73, explicit plus signs or not). A printed value no merge reproduces is reported and
left alone. Run check_numbers.py afterwards: it must pass.

Usage: uv run python scripts/paper/refresh_numbers.py --keys DIR --predictions DIR --latest aa --earlier z y x ...
"""

import argparse
import re
from pathlib import Path

from check_numbers import CLAIMS, JUDGE, PAPER

from aemon.evaluation.judging.report import report

NUMBER = r'(\$?)([+-]?)(\d+\.\d+)(\$?)'
TRIPLE = re.compile(rf'{NUMBER}(\s*\[\s*){NUMBER}(\s*,\s*){NUMBER}(\s*\])')


def triple(key: Path, predictions: Path, first: str, second: str) -> tuple[float, float, float] | None:
    """The comparison on one merge, or None when that merge does not hold both arms yet."""
    result = report(str(key), {JUDGE: str(predictions)}, (first, second))
    interval = result['judges'][JUDGE]['difference']['mean_and_95_interval']
    if interval is None:
        return None
    mean, low, high = interval
    return round(mean, 2), round(low, 2), round(high, 2)


def styled(old: tuple[str, str, str, str], value: float) -> str:
    """value written in the printed number's style: negatives always as a math-mode minus ($-0.20$), non-negatives
    with a plus sign only when the printed number carried a sign."""
    _, sign, _, _ = old
    if value < 0:
        return f'${-value:.2f}$'.replace('$', '$-', 1)
    plus = '+' if sign else ''
    return f'{plus}{value:.2f}'


def numbers_of(match: re.Match) -> tuple[float, float, float]:
    groups = match.groups()
    values = []
    for start in (0, 5, 10):
        sign, digits = groups[start + 1], groups[start + 2]
        values.append(round(float(sign + digits), 2))
    return tuple(values)


def replace_triple(tex: str, old: tuple[float, float, float], new: tuple[float, float, float]) -> tuple[str, int]:
    count = 0

    def swap(match: re.Match) -> str:
        nonlocal count
        if numbers_of(match) != old:
            return match.group(0)
        count += 1
        g = match.groups()
        parts = []
        for index, start in enumerate((0, 5, 10)):
            parts.append(styled((g[start], g[start + 1], g[start + 2], g[start + 3]), new[index]))
            if start != 10:
                parts.append(g[start + 4])
        return parts[0] + parts[1] + parts[2] + parts[3] + parts[4] + g[14]

    return TRIPLE.sub(swap, tex), count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--latest', required=True)
    parser.add_argument('--earlier', nargs='+', required=True, help='earlier merge tags, newest first')
    parser.add_argument('--paper', type=Path, default=PAPER)
    args = parser.parse_args()
    tex = args.paper.read_text()

    def files(tag: str) -> tuple[Path, Path]:
        return args.keys / f'stage2{tag}_all_key.jsonl', args.predictions / f'codexsol170_predictions_stage2{tag}_all.jsonl'

    for claim in CLAIMS:
        new = triple(*files(args.latest), claim.first, claim.second)
        done = False
        for tag in (args.latest, *args.earlier):
            old = triple(*files(tag), claim.first, claim.second)
            if old is None:
                continue
            tex, count = replace_triple(tex, old, new)
            if count:
                print(f'{claim.what}: {old} -> {new} ({count} place(s), printed from merge {tag})')
                done = True
                break
        if not done:
            print(f'{claim.what}: no printed value found from any merge; left alone')
    args.paper.write_text(tex)


if __name__ == '__main__':
    main()
