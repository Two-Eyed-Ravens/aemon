"""The no-judge columns of the ablation table (DECISIONS 19 November 20:30), one row per arm, from screen reports.

Mechanical: finished runs, stop reasons, refused calls, median model turns and peak prompt tokens per run, and how often
the agent steps acted (redrawn repeats, decide_kind replacements, abstentions and skips). Diagnostics, not evidence of
quality: evidence-kind accuracy of the accepted assessments against the dossier's annotation, split into company claims
(which evidence_first fixes) and third-party sources (the opportunities decide_kind can change), and propose or decline
against the case's test_warranted (whose labels are contestable). For every other arm, the difference in finished runs
against the reference over the cases both ran, counted per case so arms are paired by case.

Usage: python ablation_table.py --reference guards --arms guards=A_guards.json none=A_none.json ... --out table.json
"""

import argparse
import json
import statistics
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aemon.environment.cases import load_cases

EVIDENCE = Path(__file__).resolve().parents[2] / 'data' / 'dossier' / 'evidence.json'


@dataclass
class ArmRow:
    arm: str
    runs: int
    finished: int
    stop_reasons: dict[str, int]
    refused_calls: int
    median_turns: float
    median_peak_prompt_tokens: float
    redrawn_repeats: int
    decisions: dict[str, int]
    kind_accuracy_company_claims: float | None
    kind_accuracy_third_party: float | None
    third_party_assessments: int
    test_choice: dict[str, int]
    finished_minus_reference: int | None = None
    finished_by_case: dict[str, int] = field(default_factory=dict)


def gold_kinds() -> dict[str, tuple[str, str]]:
    records = json.loads(EVIDENCE.read_text())['records']
    return {r['id']: (r['kind'], r['type']) for r in records}


def accuracy(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    return sum(a == b for a, b in pairs) / len(pairs)


def decision_counts(record: dict) -> Counter[str]:
    counts: Counter[str] = Counter()
    for turn in record['model_turns']:
        made = turn.get('decision')
        if made is None:
            continue
        if made['applied']:
            counts['replaced'] += 1
        elif made['decided'] is None:
            counts['abstained'] += 1
        else:
            counts['agreed'] += 1
    return counts


def test_outcome(record: dict, warranted: bool) -> str:
    if record['tests']:
        choice = 'propose'
    elif record['test_declined']:
        choice = 'decline'
    else:
        return 'not reached'
    right = (choice == 'propose') == warranted
    return f'{choice}, {"right" if right else "wrong"}'


def arm_row(arm: str, path: str, kinds: dict[str, tuple[str, str]], warranted: dict[str, bool]) -> ArmRow:
    records = json.loads(Path(path).read_text())['records']
    company, third = [], []
    for record in records:
        for assessed in record['assessments']:
            gold, source_type = kinds.get(assessed['evidence_id'], (None, None))
            if gold is None:
                continue
            target = company if source_type == 'company_claim' else third
            target.append((assessed['evidence_kind'], gold))
    peaks = [max((t.get('prompt_tokens') or 0 for t in r['model_turns']), default=0) for r in records]
    by_case: dict[str, list[int]] = {}
    for record in records:
        by_case.setdefault(record['case'], []).append(record['stop_reason'] == 'finished')
    decisions: Counter[str] = Counter()
    for record in records:
        decisions += decision_counts(record)
    return ArmRow(
        arm=arm,
        runs=len(records),
        finished=sum(r['stop_reason'] == 'finished' for r in records),
        stop_reasons=dict(Counter(r['stop_reason'] for r in records)),
        refused_calls=sum(not c.get('accepted') for r in records for c in r['calls'] if not c.get('harness')),
        median_turns=statistics.median(len(r['model_turns']) for r in records),
        median_peak_prompt_tokens=statistics.median(peaks),
        redrawn_repeats=sum(t.get('redraws', 0) for r in records for t in r['model_turns']),
        decisions=dict(decisions),
        kind_accuracy_company_claims=accuracy(company),
        kind_accuracy_third_party=accuracy(third),
        third_party_assessments=len(third),
        test_choice=dict(Counter(test_outcome(r, warranted[r['case']]) for r in records)),
        finished_by_case={case: sum(done) for case, done in by_case.items()},
    )


def markdown(rows: list[ArmRow]) -> str:
    header = '| Arm | Finished | vs reference | Context limit | Refused | Median turns | Redraws | decide_kind replaced / abstained | Kind acc., third party |'
    lines = [header, '|' + '---|' * 9]
    for row in rows:
        diff = '' if row.finished_minus_reference is None else f'{row.finished_minus_reference:+d}'
        third = '' if row.kind_accuracy_third_party is None else f'{row.kind_accuracy_third_party:.0%} of {row.third_party_assessments}'
        made = f'{row.decisions.get("replaced", 0)} / {row.decisions.get("abstained", 0)}' if row.decisions else ''
        context = row.stop_reasons.get('context limit', 0)
        lines.append(
            f'| {row.arm} | {row.finished}/{row.runs} | {diff} | {context} | {row.refused_calls} | {row.median_turns:g} | {row.redrawn_repeats} | {made} | {third} |'
        )
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--arms', nargs='+', required=True, help='name=screen report JSON')
    parser.add_argument('--reference', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    kinds = gold_kinds()
    warranted = {c.id: c.test_warranted for c in load_cases()}
    rows = [arm_row(*spec.split('=', 1), kinds, warranted) for spec in args.arms]
    reference = next(r for r in rows if r.arm == args.reference)
    for row in rows:
        if row is reference:
            continue
        shared = sorted(set(row.finished_by_case) & set(reference.finished_by_case))
        row.finished_minus_reference = sum(row.finished_by_case[c] - reference.finished_by_case[c] for c in shared)
    Path(args.out).write_text(json.dumps([asdict(r) for r in rows], indent=1))
    Path(args.out).with_suffix('.md').write_text(markdown(rows) + '\n')
    print(markdown(rows))


if __name__ == '__main__':
    main()
