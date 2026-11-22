#!/bin/bash
# The single test set 3 run (DECISIONS, 20 November: 14:05, 14:12, 18:28 and the two-judge entry). Run only after
# Hatem's Monday confirmation, the frozen configuration commit, a fresh deploy of REVISION to both accounts and a
# passing scripts/test3/preflight.sh REVISION.
#   Arms, 48 cases x 2 attempts each: A (Aya Expanse 8B + A's seed-7 adapter, no decide_kind), the prompted 8B on the
#   same scaffold (compact prompt, six guards, 8,192 context; only the adapter differs), and the Stage 1 system
#   (Tiny Aya, version 1 and 3 adapters routed as before, the same six guards; jobs/eval_switch.sbatch).
#   Then one blind shuffled packet set for all three, both judges, and scripts/test3/analyze.py.
# Usage: scripts/test3/run_test3.sh REVISION     Stops with a message at the first failure; safe to rerun the later steps.
# ssh -n: without it ssh reads the jobs.txt lines the wait loop is iterating over (22 November, first attempt)
set -u
REV=${1:?code revision}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
HR=5062468bf9bc0c6035fd64e06274333ec127d980
GUARDS=no_repeats,quote_menu,resample_repeats,budget,grounded_beliefs,evidence_first
STAGE1_ROUTE='default=1,brief=0,frame=0,evidence=0'
OUT=$REPO/experiments/test3
KEY=$HOME/lexsi-backup/judge_keys/test3_key.jsonl
RES=$HOME/lexsi-backup/judge_results/test3
H() { ssh -n -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi" CLUSTER_ACCOUNT@CLUSTER_HOST "$1"; }
N() { ssh -n -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi2" CLUSTER_ACCOUNT_2@CLUSTER_HOST "$1"; }
cd "$REPO" || exit 1
CASES=$(python3 -c "import json; c=json.load(open('data/dossier/cases_heldout3.json')); c=c if isinstance(c, list) else c.get('cases', c); c=c if isinstance(c, list) else list(c.values()); print(','.join(x['id'] for x in c))")
[ "$(echo "$CASES" | tr ',' '\n' | wc -l)" = 48 ] || { echo "expected 48 test set 3 cases"; exit 1; }
mkdir -p "$OUT" "$RES"
state() { $1 "sacct -j $2 -n -X -o State | head -1 | tr -d ' '"; }
wait_done() {  # account function, job
  local s
  while true; do
    s=$(state "$1" "$2")
    case "$s" in COMPLETED) return 0 ;; FAILED|TIMEOUT|OUT_OF_ME*|CANCELLED*|NODE_FAIL) echo "job $2 ended $s"; return 1 ;; esac
    sleep 300
  done
}
screen() {  # account function, name, adapter path or empty, route or empty, python
  local adapter=${3:+ADAPTER=$3} route=${4:+ROUTE=$4}
  $1 "cd ~/lexsi/code_$REV && NAME=$2 HF_REPO=CohereLabs/aya-expanse-8b HF_REV=$HR PY=$5 $adapter $route PROMPT=compact ARMS=guards CONTEXT=8192 SPLIT=heldout3 ATTEMPTS=2 CASES='$CASES' REVISION=$REV sbatch --parsable --export=ALL jobs/screen_bases.sbatch"
}
if [ ! -s "$OUT/jobs.txt" ]; then
  JA=$(screen N test3-A '$HOME/lexsi/runs/base_aya-expanse-8b/adapter.gguf' default=0 '$HOME/lexsi/env_train/bin/python')
  JP=$(screen H test3-prompted '' '' '$HOME/lexsi/env/bin/python')
  JS=$(H "cd ~/lexsi/code_$REV && NAME=test3-stage1 ROUTE='$STAGE1_ROUTE' RECOVERY=$GUARDS SPLIT=heldout3 ATTEMPTS=2 CASES='$CASES' REVISION=$REV sbatch --parsable --export=ALL jobs/eval_switch.sbatch")
  [ -n "$JA" ] && [ -n "$JP" ] && [ -n "$JS" ] || { echo "a submission failed: A=$JA prompted=$JP stage1=$JS"; exit 1; }
  printf 'A N %s\nprompted H %s\nstage1 H %s\n' "$JA" "$JP" "$JS" > "$OUT/jobs.txt"
  echo "$(date +%H:%M) submitted: A $JA (N), prompted $JP (H), stage1 $JS (H)"
fi
while read -r arm acct job; do wait_done "$acct" "$job" || exit 1; done < "$OUT/jobs.txt"
scp -q -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi2" CLUSTER_ACCOUNT_2@CLUSTER_HOST:lexsi/runs/screen/test3-A_guards.json "$OUT/A.json" || exit 1
scp -q -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi" CLUSTER_ACCOUNT@CLUSTER_HOST:lexsi/runs/screen/test3-prompted_guards.json "$OUT/prompted.json" || exit 1
scp -q -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi" CLUSTER_ACCOUNT@CLUSTER_HOST:lexsi/runs/eval/test3-stage1.json "$OUT/stage1.json" || exit 1
for arm in A prompted stage1; do
  python3 -c "import json; d=json.load(open('$OUT/$arm.json')); s=d['summary']; a=d.get('auditkit') or {}; print('$arm', s['finished'], 'of', s['episodes'], 'finished;', 'AuditKIT', 'SKIPPED' if 'skipped' in a else 'ok')"
done
[ -s "$OUT/packets.jsonl" ] || PYTHONPATH=src .venv/bin/python -m aemon.evaluation.judging.packets --split heldout3 \
  --report A="$OUT/A.json" --report prompted="$OUT/prompted.json" --report stage1="$OUT/stage1.json" --packets "$OUT/packets.jsonl" --key "$KEY" || exit 1
for judge in codexsol170 claudecode; do
  [ -s "$RES/$judge/predictions.jsonl" ] && continue
  PYTHONPATH=src .venv/bin/python src/aemon/evaluation/judging/judge_v1/run_campaign.py --backend $judge --packets "$OUT/packets.jsonl" \
    --output "$RES/$judge" --qualification reports/judge/${judge}_score_qualification.json --workers 4 > "$OUT/${judge}_run.log" 2>&1 || { echo "$judge campaign failed"; exit 1; }
  echo "$(date +%H:%M) $judge: $(grep -c '"valid": true' "$OUT/${judge}_run.log") valid, $(grep -c '"valid": false' "$OUT/${judge}_run.log") invalid"
done
PYTHONPATH=src .venv/bin/python scripts/test3/analyze.py --key "$KEY" --judge codexsol170="$RES/codexsol170/predictions.jsonl" \
  --judge claudecode="$RES/claudecode/predictions.jsonl" --compare A,prompted --compare A,stage1 --out "$OUT/report.json" > /dev/null || exit 1
echo "$(date +%H:%M) done: $OUT/report.json"
