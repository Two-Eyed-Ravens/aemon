#!/bin/bash
# The fine-tuned 8B without guards as a fifth test set 3 arm (DECISIONS 23 November, registered before the run): wait
# for the cluster job, fetch its report, rebuild packets with the three original arms, reuse their judgments by packet
# id, judge only the new packets blind with both judges (a failed answer re-judged once), then scripts/test3/analyze.py
# unchanged with A minus A-without-guards and A-without-guards minus the prompted 8B.
set -uo pipefail
cd "$(dirname "$0")/../../.."
O=experiments/test3/noguards T=experiments/test3 JOB=786573
K=$HOME/lexsi-backup/judge_keys/test3_noguards_key.jsonl R=$HOME/lexsi-backup/judge_results/test3_noguards
SSH="ssh -n -o ControlMaster=no -o ConnectTimeout=20 -o ControlPath=$HOME/.ssh/cm-lexsi2 CLUSTER_ACCOUNT_2@CLUSTER_HOST"
while true; do
  s=$(timeout 40 $SSH "sacct -j $JOB -X -n -o State | head -1" 2>/dev/null | tr -d ' ')
  case "$s" in COMPLETED) break ;; FAILED|CANCELLED*|TIMEOUT|OUT_OF_ME*|NODE_FAIL) echo "job $JOB ended $s"; exit 1 ;; esac
  sleep 300
done
echo "$(date +%H:%M) job done"
for f in test3-A-noguards_none.json test3-A-noguards_none.episodes.jsonl test3-A-noguards_none.log; do
  timeout 300 scp -q -o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-lexsi2 CLUSTER_ACCOUNT_2@CLUSTER_HOST:lexsi/runs/screen/$f $O/ || { echo "fetch $f failed"; exit 1; }
done
mkdir -p $R
PYTHONPATH=src .venv/bin/python -W ignore -m aemon.evaluation.judging.packets --split heldout3 --report A=$T/A.json \
  --report prompted=$T/prompted.json --report stage1=$T/stage1.json --report A_noguards=$O/test3-A-noguards_none.json \
  --packets $O/packets.jsonl --key $K || exit 1
.venv/bin/python - $O $T <<'PY'
import json, sys
O, T = sys.argv[1:]
old = {json.loads(l)['packet_id'] for l in open(f'{T}/packets.jsonl')}
new = [l for l in open(f'{O}/packets.jsonl') if json.loads(l)['packet_id'] not in old]
open(f'{O}/packets_new.jsonl', 'w').writelines(new)
print(json.dumps({'new_packets': len(new)}))
PY
judge() {  # backend
  PYTHONPATH=src .venv/bin/python src/aemon/evaluation/judging/judge_v1/run_campaign.py --backend $1 --packets $O/packets_new.jsonl \
    --output $R/$1 --qualification reports/judge/$1_score_qualification.json --workers 4 > $O/$1_run.log 2>&1
  bad=$(grep '"valid": false' $O/$1_run.log | grep -o '"packet": "[0-9a-f]*"' | cut -d'"' -f4)
  if [ -n "$bad" ]; then
    mkdir -p $R/invalid_first/$1
    for p in $bad; do mv $R/$1/$p $R/invalid_first/$1/; done
    mv $R/$1/predictions.jsonl $R/invalid_first/$1/predictions_first.jsonl
    PYTHONPATH=src .venv/bin/python src/aemon/evaluation/judging/judge_v1/run_campaign.py --backend $1 --packets $O/packets_new.jsonl \
      --output $R/$1 --qualification reports/judge/$1_score_qualification.json --workers 3 > $O/$1_rejudge.log 2>&1
  fi
  echo "$1: $(grep -c '"valid": true' $O/$1_run.log) valid first, $(echo "$bad" | grep -c .) re-judged"
}
judge codexsol170 & judge claudecode & wait
cp $K $O/test3_noguards_key.jsonl
mkdir -p $O/judging
for j in codexsol170 claudecode; do
  cat $T/judging/${j}_predictions.jsonl $R/$j/predictions.jsonl > $O/judging/${j}_predictions.jsonl
done
PYTHONPATH=src .venv/bin/python scripts/test3/analyze.py --key $O/test3_noguards_key.jsonl \
  --judge codexsol170=$O/judging/codexsol170_predictions.jsonl --judge claudecode=$O/judging/claudecode_predictions.jsonl \
  --compare A,A_noguards --compare A_noguards,prompted --out $O/report.json > /dev/null && echo "$(date +%H:%M) report: $O/report.json"
