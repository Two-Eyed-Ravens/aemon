"""Figure: each effect at every training seed, computed from the combined judge key and predictions (repeated judgments
of a packet averaged, as registered), development, one judge. Rows: fine-tuning (A against the prompted 8B), recovery
rows (B minus A, matched seed) and the decision model (on minus off), one point per seed or agent with its 95% interval.
Comparisons whose arms are not judged yet are skipped.

Usage: uv run --with matplotlib python scripts/paper/fig_seeds.py --key KEY.jsonl --predictions PRED.jsonl
"""

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from aemon.evaluation.judging.report import report

OUT = Path('docs/stage2/figures/fig_seeds.pdf')
INK, MUTED, GRID = '#1f2933', '#9aa5b1', '#e4e7eb'


@dataclass(frozen=True)
class Row:
    group: str
    label: str
    first: str
    second: str


ROWS = [
    Row('Fine-tuning', 'seed 7', 'ayaA7_guards', 'ayaP_compact_guards'),
    Row('Fine-tuning', 'seed 11', 'ayaA11_guards', 'ayaP_compact_guards'),
    Row('Fine-tuning', 'seed 13', 'ayaA13_guards', 'ayaP_compact_guards'),
    Row('Recovery rows', 'seed 7', 'ayaB7_guards', 'ayaA7_guards'),
    Row('Recovery rows', 'seed 11', 'ayaB11_guards', 'ayaA11_guards'),
    Row('Recovery rows', 'seed 13', 'ayaB13_guards', 'ayaA13_guards'),
    Row('Decision model', 'A, seed 7', 'ayaA7_decide', 'ayaA7_guards'),
    Row('Decision model', 'A, seed 11', 'ayaA11_decide', 'ayaA11_guards'),
    Row('Decision model', 'A, seed 13', 'ayaA13_decide', 'ayaA13_guards'),
    Row('Decision model', 'B, seed 7', 'ayaB7_decide', 'ayaB7_guards'),
    Row('Decision model', 'B, seed 11', 'ayaB11_decide', 'ayaB11_guards'),
    Row('Decision model', 'prompted 8B', 'ayaP_compact_decide', 'ayaP_compact_guards'),
]


def effects(key: str, predictions: str) -> list[tuple[Row, list[float]]]:
    found = []
    for row in ROWS:
        result = report(key, {'codexsol170': predictions}, (row.first, row.second))
        difference = result['judges']['codexsol170'].get('difference', {})
        interval = difference.get('mean_and_95_interval')
        if interval:
            found.append((row, interval))
    return found


def draw(found: list[tuple[Row, list[float]]]) -> None:
    fig, ax = plt.subplots(figsize=(3.2, 0.24 * len(found) + 0.9), dpi=200)
    labels = []
    for y, (row, (mean, low, high)) in enumerate(reversed(found)):
        ax.plot([low, high], [y, y], '-', lw=1.6, color=INK, solid_capstyle='round')
        ax.plot(mean, y, 'o', ms=4.5, color=INK)
        ax.text(1.12, y, f'{mean:+.2f}', va='center', fontsize=6.5, color=INK)
        labels.append(f'{row.group}: {row.label}')
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_yticks(range(len(found)))
    ax.set_yticklabels(labels, fontsize=6.5)
    ax.set_xlim(-0.45, 1.25)
    ax.set_xticks([0, 0.5, 1.0])
    ax.tick_params(axis='x', labelsize=6.5)
    ax.set_xlabel('Paired difference in judge score', fontsize=6.5)
    ax.grid(axis='x', color=GRID, lw=0.5)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', required=True)
    parser.add_argument('--predictions', required=True)
    args = parser.parse_args()
    found = effects(args.key, args.predictions)
    draw(found)
    for row, interval in found:
        print(f'{row.group:15s} {row.label:12s} {interval[0]:+.2f} [{interval[1]:+.2f}, {interval[2]:+.2f}]')
    print('saved', OUT)


if __name__ == '__main__':
    main()
