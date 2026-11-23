#!/bin/bash
# One of the two prompted-8B arms added to test set 3 (DECISIONS 23 November, registered before their runs): wait for
# its cluster job, fetch the report, rebuild packets with A, the prompted 8B and A without guards, reuse every existing
# judgment by packet id, judge only the new packets blind with both judges (a failed answer re-judged once), then
# scripts/test3/analyze.py unchanged.
# Usage: run_after.sh ARM ACCOUNT CONTROLPATH JOB REPORT COMPARE...
#   e.g. run_after.sh P_compact_none CLUSTER_ACCOUNT_2 cm-lexsi2 787455 test3-prompted-compact-noguards_none.json A,P_compact_none
set -uo pipefail
cd "$(dirname "$0")/../../.."
ARM=$1 ACCT=$2 CP=$3 JOB=$4 REPORT=$5; shift 5
O=experiments/test3/prompted_more/$ARM T=experiments/test3 G=experiments/test3/noguards
K=$HOME/lexsi-backup/judge_keys/test3_${ARM}_key.jsonl R=$HOME/lexsi-backup/judge_results/test3_$ARM
SSH="ssh -n -o ControlMaster=no -o ConnectTimeout=20 -o ControlPath=$HOME/.ssh/$CP $ACCT@CLUSTER_HOST"
mkdir -p $O $R
while true; do
  s=$(timeout 40 $SSH "sacct -j $JOB -X -n -o State | head -1" 2>/dev/null | tr -d ' ')
  case "$s" in COMPLETED) break ;; FAILED|CANCELLED*|TIMEOUT|OUT_OF_ME*|NODE_FAIL) echo "job $JOB ended $s"; exit 1 ;; esac
  sleep 300
done
echo "$(date +%H:%M) $ARM job done"
timeout 300 scp -q -o ControlMaster=no -o ControlPath=$HOME/.ssh/$CP $ACCT@CLUSTER_HOST:lexsi/runs/screen/$REPORT $O/ || { echo "fetch failed"; exit 1; }
PYTHONPATH=src .venv/bin/python -W ignore -m aemon.evaluation.judging.packets --split heldout3 --report A=$T/A.json \
  --report prompted=$T/prompted.json --report A_noguards=$G/test3-A-noguards_none.json --report $ARM=$O/$REPORT \
  --packets $O/packets.jsonl --key $K || exit 1
.venv/bin/python - $O $T $G <<'PY'
import json, sys
O, T, G = sys.argv[1:]
old = {json.loads(l)['packet_id'] for f in (f'{T}/packets.jsonl', f'{G}/packets.jsonl') for l in open(f)}
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
cp $K $O/test3_${ARM}_key.jsonl
mkdir -p $O/judging
for j in codexsol170 claudecode; do
  cat $T/judging/${j}_predictions.jsonl $HOME/lexsi-backup/judge_results/test3_noguards/$j/predictions.jsonl $R/$j/predictions.jsonl > $O/judging/${j}_predictions.jsonl
done
CMP=(); for c in "$@"; do CMP+=(--compare "$c"); done
PYTHONPATH=src .venv/bin/python scripts/test3/analyze.py --key $O/test3_${ARM}_key.jsonl \
  --judge codexsol170=$O/judging/codexsol170_predictions.jsonl --judge claudecode=$O/judging/claudecode_predictions.jsonl \
  "${CMP[@]}" --out $O/report.json > /dev/null && echo "$(date +%H:%M) report: $O/report.json"
