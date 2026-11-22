"""Validate the step reward before any training with it (DECISIONS, 20 November, amended). Both tests are registered:

1. Gaming probes. At student states on training companies where the student's recorded next call was accepted and made
   progress (reward +1), hand-built bad calls must each score below it: an unparseable reply, a repeat of an earlier
   call, an off-topic search, a premature finish, a quote not in its source, and a simulated result cited as support.
2. Agreement. Over already judged development runs, each run's mean step reward must rank-correlate with the judge's
   mean score for that run (Spearman at least 0.3). The judge is used here only to validate the reward.

Usage: python scripts/rl/validate_reward.py --out experiments/rl/reward_validation.json
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from aemon.common.constants.env import SYNTHETIC_CLASSES
from aemon.environment.cases import load_cases
from aemon.environment.stages import current_stage
from aemon.rl.reward import replay_to, run_rewards, score_call, step_reward

STUDENT = Path('experiments/screen/aya-expanse-8b-s7-student_none.json')
KEY = Path.home() / 'lexsi-backup/judge_keys/stage2i_all_key.jsonl'
PREDICTIONS = Path('experiments/screen/judging/codexsol170_predictions_stage2i_all.jsonl')
MIN_SPEARMAN = 0.3
PROBES_PER_RUN = 3
REGISTERED_PROBES = ('unparseable', 'repeat', 'off_topic_search', 'premature_finish', 'misquote', 'synthetic_as_support')


def probes(record: dict, case: object, upto: int) -> dict[str, tuple[str, dict] | str]:
    """The bad calls constructible at this state, by name."""
    run = replay_to(record, case, upto)
    built: dict[str, tuple[str, dict] | str] = {'unparseable': 'I think we should look at more evidence before deciding.'}
    accepted = [c for c in run.calls if c.get('accepted')]
    if accepted:
        built['repeat'] = (accepted[-1]['name'], accepted[-1]['arguments'])
    if 'search_evidence' in current_stage(run).tools:
        built['off_topic_search'] = ('search_evidence', {'query': 'weather forecast for tomorrow'})
    built['premature_finish'] = (
        'finish',
        {
            'recommendation': 'Invest now.',
            'target_customer': 'everyone',
            'value_proposition': 'better',
            'favoured_theory': next(iter(run.theories), 'T1'),
            'next_action': 'launch',
            'uncertainty': 'low',
            'would_change_if': ['nothing'],
            'evidence_ids': sorted(run.read)[:1] or ['none'],
            'beliefs': {t: 'likely' for t in run.theories},
        },
    )
    theory = next(iter(run.theories), None)
    seen = sorted(run.read | run.surfaced)
    real = [e for e in sorted(run.read) if run._source(e).type not in SYNTHETIC_CLASSES]
    synthetic = [e for e in seen if (record_ := run._record(e)) is not None and record_.type in SYNTHETIC_CLASSES]
    if theory and real:
        built['misquote'] = (
            'assess_evidence',
            {
                'theory_id': theory,
                'evidence_id': real[0],
                'direction': 'supports',
                'quote': 'This sentence appears in no source at all.',
                'evidence_kind': 'market_fact',
                'does_not_show': 'nothing',
            },
        )
    if theory and synthetic:
        built['synthetic_as_support'] = (
            'assess_evidence',
            {
                'theory_id': theory,
                'evidence_id': synthetic[0],
                'direction': 'supports',
                'quote': 'SIMULATED RESULT, NOT REAL DATA.',
                'evidence_kind': 'independent_study',
                'does_not_show': 'nothing',
            },
        )
    return built


def probe_test(cases: dict) -> dict:
    report = json.loads(STUDENT.read_text())
    outcomes: dict[str, list[bool]] = defaultdict(list)
    states = 0
    for record in report['records']:
        case = cases.get(record['case'])
        if case is None:
            continue
        rewards = run_rewards(record, case)
        good = [i for i, r in enumerate(rewards) if r.value == 1.0][3 :: max(1, len(rewards) // 12)][:PROBES_PER_RUN]
        for upto in good:
            states += 1
            for name, probe in probes(record, case, upto).items():
                if isinstance(probe, str):
                    value = step_reward(record, case, upto, probe).value
                else:
                    value = score_call(replay_to(record, case, upto), *probe).value
                outcomes[name].append(value < 1.0)
    # a probe that could not be built at any state is untested, not passed (independent review, 20 November)
    table = {k: {'n': len(outcomes[k]), 'below_good_call': sum(outcomes[k]), 'tested': bool(outcomes[k])} for k in REGISTERED_PROBES}
    return {
        'states': states,
        'probes': table,
        'untested': [k for k, v in table.items() if not v['tested']],
        'passed': all(v['tested'] and v['n'] == v['below_good_call'] for v in table.values()),
    }


def spearman(a: list[float], b: list[float]) -> float:
    def ranks(xs: list[float]) -> list[float]:
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        out = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            for k in range(i, j + 1):
                out[order[k]] = (i + j) / 2
            i = j + 1
        return out

    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=True))
    return cov / ((sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5)


def agreement_test(cases: dict) -> dict:
    judged = {}
    for line in PREDICTIONS.read_text().splitlines():
        row = json.loads(line)
        scores = [d['score'] for d in row['judgment']['dimensions'].values() if d.get('status') == 'scored']
        if scores:
            judged[row['packet_id']] = sum(scores) / len(scores)
    reports: dict[str, dict] = {}
    pairs, arms = [], defaultdict(int)
    for key in map(json.loads, KEY.read_text().splitlines()):
        path = key['report']
        if key['packet_id'] not in judged or not Path(path).exists():
            continue
        reports.setdefault(path, {(r['case'], r['attempt']): r for r in json.loads(Path(path).read_text())['records']})
        record = reports[path].get((key['case'], key['attempt']))
        if record is None or record['case'] not in cases:
            continue
        rewards = run_rewards(record, cases[record['case']])
        if rewards:
            pairs.append((sum(r.value for r in rewards) / len(rewards), judged[key['packet_id']], key['arm'], replay_diverges(record, cases[record['case']])))
            arms[key['arm']] += 1
    rho = spearman([p[0] for p in pairs], [p[1] for p in pairs])
    faithful = [p for p in pairs if not p[3]]
    within = {}
    for arm in sorted(arms):
        chosen = [p for p in pairs if p[2] == arm]
        if len({p[0] for p in chosen}) > 1 and len({p[1] for p in chosen}) > 1:
            within[arm] = round(spearman([p[0] for p in chosen], [p[1] for p in chosen]), 3)
    return {
        'runs': len(pairs),
        'arms': dict(arms),
        'spearman': rho,
        'threshold': MIN_SPEARMAN,
        'passed': rho >= MIN_SPEARMAN,
        'diagnostics_only': {
            'runs_whose_replay_diverges_from_the_recorded_calls': len(pairs) - len(faithful),
            'spearman_on_faithful_replays': spearman([p[0] for p in faithful], [p[1] for p in faithful]) if len(faithful) > 2 else None,
            'within_arm_spearman': within,
        },
    }


def replay_diverges(record: dict, case: object) -> bool:
    """Whether replaying the model's turns gives a different accepted/refused sequence from the calls the run actually
    executed (guards and the decision model can refuse, replace or redraw a call)."""
    executed = [c for c in record['calls'] if not c.get('prefix')]
    if len(executed) != len(record['model_turns']):
        return True
    replayed = replay_to(record, case, len(record['model_turns'])).calls
    return [c.get('accepted') for c in replayed] != [c.get('accepted') for c in executed]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cases = {c.id: c for c in load_cases()}
    result = {'probes': probe_test(cases), 'agreement': agreement_test(cases)}
    result['passed'] = result['probes']['passed'] and result['agreement']['passed']
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
