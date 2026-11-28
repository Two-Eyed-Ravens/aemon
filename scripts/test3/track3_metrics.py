"""The Track 3 metrics on test set 3 for every arm, with Stage 1's definitions (scripts/release/track3_metrics.py): task
success (finished investigations), tool-call accuracy (accepted calls over all calls), calls per finished run, and
latency as the model time each run recorded (the sum of its turns' seconds; median over runs). The arms ran on
different hardware and serving setups (A100 slices for the local models, Anthropic's API for Haiku), so latency is
rough.

Usage: uv run python scripts/test3/track3_metrics.py  -> experiments/test3/track3_metrics.json, a markdown table on stdout
"""

import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST3 = ROOT / 'experiments' / 'test3'
ARMS = {
    'Prompted Aya Expanse 8B': TEST3 / 'prompted.json',
    'Stage 1 system (Tiny Aya 3.35B)': TEST3 / 'stage1.json',
    'Fine-tuned Aya Expanse 8B (A)': TEST3 / 'A.json',
    'A at 4 bits, merged, 8 at once': TEST3 / 'q4' / 'q4_k_m_s8.json',
    'Claude Haiku 5.5': TEST3 / 'haiku' / 'haiku_merged.json',
}


@dataclass(frozen=True)
class ArmMetrics:
    runs: int
    finished: int
    task_success: float
    calls: int
    accepted: int
    tool_call_accuracy: float
    calls_per_finished_run: float
    median_seconds_per_run: float


def run_seconds(record: dict) -> float:
    return sum(turn.get('seconds') or 0.0 for turn in record['model_turns'])


def metrics(records: list[dict]) -> ArmMetrics:
    finished = sum(r['stop_reason'] == 'finished' for r in records)
    calls = sum(len(r['calls']) for r in records)
    accepted = sum(sum(1 for c in r['calls'] if c['accepted']) for r in records)
    return ArmMetrics(
        runs=len(records),
        finished=finished,
        task_success=finished / len(records),
        calls=calls,
        accepted=accepted,
        tool_call_accuracy=accepted / calls,
        calls_per_finished_run=calls / finished,
        median_seconds_per_run=statistics.median(run_seconds(r) for r in records),
    )


def main() -> None:
    table = {arm: metrics(json.loads(path.read_text())['records']) for arm, path in ARMS.items()}
    out = TEST3 / 'track3_metrics.json'
    out.write_text(json.dumps({arm: asdict(m) for arm, m in table.items()}, indent=1) + '\n')
    print('| Arm | Task success | Tool-call accuracy | Calls per finished run | Median model seconds per run |')
    print('|---|---|---|---|---|')
    for arm, m in table.items():
        success = f'{m.finished} of {m.runs} ({100 * m.task_success:.0f}%)'
        print(f'| {arm} | {success} | {100 * m.tool_call_accuracy:.1f}% | {m.calls_per_finished_run:.0f} | {m.median_seconds_per_run:.0f} |')


if __name__ == '__main__':
    main()
