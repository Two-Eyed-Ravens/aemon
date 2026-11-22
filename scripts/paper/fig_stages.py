"""Figure 1: how far each agent gets. For every run of an arm, which stages of the investigation it completed, in the
stage controller's order (aemon.environment.stages), as a share of the arm's runs. All runs, not a chosen example:
development, 15 cases x 3 attempts, the same scaffold, guards and server for the first two arms.

Usage: uv run --with matplotlib python scripts/paper/fig_stages.py
"""

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCREEN = Path('experiments/screen')
OUT = Path('docs/stage2/figures/fig_stages.pdf')
INK, MUTED, GRID = '#1f2933', '#616e7c', '#e4e7eb'
STAGES = ('framed', 'read evidence', 'two theories', 'assessed', 'challenged', 'test or decline', 'position', 'finished')


@dataclass(frozen=True)
class Arm:
    label: str
    report: str
    colour: str
    marker: str
    # where the direct label sits, in data coordinates (stage index, percent), chosen so no label crosses a line
    label_at: tuple[float, float]


# Okabe-Ito colours, fixed order: colour-blind safe, and each line also has its own marker and a direct label
ARMS = (
    Arm('prompted 8B', 'aya-expanse-8b-prompted-compact_guards.json', '#E69F00', 's', (4.9, 8)),
    Arm('fine-tuned, no guards', 'aya-expanse-8b-s7-abl1_none.json', '#009E73', '^', (1.9, 64)),
    Arm('fine-tuned (A)', 'aya-expanse-8b-s7_guards.json', '#0072B2', 'o', (3.0, 104)),
)


def completed(record: dict) -> list[bool]:
    tested = bool(record['tests']) or record['test_declined'] is not None
    return [
        bool(record['frame']),
        bool(record['read']),
        len(record['theories']) >= 2,
        bool(record['assessments']),
        bool(record['challenge_searches']),
        tested,
        bool(record['position']),
        record['stop_reason'] == 'finished',
    ]


def shares(path: Path) -> tuple[list[float], int]:
    records = json.loads(path.read_text())['records']
    rows = [completed(r) for r in records]
    return [sum(r[i] for r in rows) / len(rows) for i in range(len(STAGES))], len(rows)


def main() -> None:
    plt.rcParams.update({'font.size': 7.5, 'font.family': 'serif', 'axes.edgecolor': MUTED, 'axes.labelcolor': INK})
    fig, ax = plt.subplots(figsize=(3.3, 1.9))
    x = range(len(STAGES))
    summary = {}
    for arm in ARMS:
        values, n = shares(SCREEN / arm.report)
        summary[arm.label] = {'runs': n, 'shares': dict(zip(STAGES, values, strict=True))}
        ax.plot(x, [100 * v for v in values], color=arm.colour, marker=arm.marker, markersize=3.5, linewidth=1.2)
        ax.text(*arm.label_at, f'{arm.label}: {100 * values[-1]:.0f}% finish', fontsize=6.5, color=INK, ha='center')
    ax.set_xticks(list(x), STAGES, rotation=35, ha='right', fontsize=6.5)
    ax.set_ylabel('runs reaching it (%)')
    ax.set_ylim(0, 112)
    ax.grid(axis='y', color=GRID, linewidth=0.5)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(colors=MUTED, labelcolor=INK)
    fig.tight_layout(pad=0.3)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    fig.savefig(OUT.with_suffix('.png'), dpi=200)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
