"""Figure: paired effects of fine-tuning, recovery rows, the decision model and the 8B system against version 1, from the
judge reports in experiments/screen/judging/ (development, one judge). Writes a wide PNG for documents and a
column-width PDF for the paper. Usage: uv run --with matplotlib python scripts/paper/fig_effects.py
"""

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

JUDGING = Path('experiments/screen/judging')
FIGURES = Path('docs/stage2/figures')
INK, MUTED, GRID = '#1f2933', '#9aa5b1', '#e4e7eb'


@dataclass(frozen=True)
class Effect:
    wide_label: str
    column_label: str
    report: str


EFFECTS = [
    Effect('Fine-tuning, same scaffold\n(A vs prompted 8B)', 'Fine-tuning\n(A vs prompted)', 'report_ayaA7guards_vs_ayaPcompactguards.json'),
    Effect('Recovery rows\n(B vs A)', 'Recovery rows\n(B vs A)', 'report_ayaB7guards_vs_ayaA7_guards.json'),
    Effect('Decision model\n(A + decide_kind vs A)', 'Decision model\n(on vs off, A)', 'report_ayaA7decide_vs_ayaA7_guards.json'),
    Effect('8B system vs Stage 1 system\n(B vs version 1)', '8B vs Stage 1\n(B vs v1)', 'report_ayaB7guards_vs_final_system.json'),
]


def draw(size: tuple[float, float], font: float, column: bool, out: Path) -> None:
    fig, ax = plt.subplots(figsize=size, dpi=200)
    label_x = 1.08 if column else 1.18
    for i, effect in enumerate(EFFECTS):
        report = json.loads((JUDGING / effect.report).read_text())
        difference = report['judges']['codexsol170']['difference']
        mean, low, high = difference['mean_and_95_interval']
        y = len(EFFECTS) - 1 - i
        for company_mean in difference['by_company'].values():
            ax.plot(company_mean, y, 'o', ms=font * 0.45, color=MUTED, zorder=2)
        ax.plot([low, high], [y, y], '-', lw=1.8, color=INK, zorder=3, solid_capstyle='round')
        ax.plot(mean, y, 'o', ms=font * 0.8, color=INK, zorder=4)
        ax.text(
            label_x, y, f'{mean:+.2f}\n[{low:+.2f}, {high:+.2f}]' if column else f'{mean:+.2f} [{low:+.2f}, {high:+.2f}]', va='center', fontsize=font, color=INK
        )
    labels = [e.column_label if column else e.wide_label for e in EFFECTS]
    ax.axvline(0, color=MUTED, lw=1, zorder=1)
    ax.set_yticks(range(len(EFFECTS)))
    ax.set_yticklabels(labels[::-1], fontsize=font)
    ax.set_xlim(-0.35, 1.55 if column else 1.65)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0] if column else [-0.25, 0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='x', labelsize=font)
    ax.set_xlabel(
        'Paired difference in judge score' if column else 'Paired difference in blind judge score (0-3 rubric); dots: the six companies', fontsize=font
    )
    ax.grid(axis='x', color=GRID, lw=0.6, zorder=0)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    if not column:
        ax.set_title('Development, one judge, 45 runs per arm, training seed 7 (exploratory until seeds 11, 13)', fontsize=font, color=INK, loc='left')
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main() -> None:
    draw((7.2, 3.6), 8, False, FIGURES / 'fig_effects_seed7.png')
    draw((3.15, 2.7), 7, True, FIGURES / 'fig_effects_seed7_col.pdf')
    print('saved')


if __name__ == '__main__':
    main()
