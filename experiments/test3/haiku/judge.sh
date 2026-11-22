#!/bin/bash
# Haiku 5.5 as a fourth test set 3 arm (DECISIONS 22 November, registered before the run): packets rebuilt from all four
# arms, judgments of packets already judged reused by packet id, only the new packets judged blind by both judges, then
# scripts/test3/analyze.py unchanged with Haiku minus A and Haiku minus the Stage 1 system.
set -uo pipefail
cd "$(dirname "$0")/../../.."
O=experiments/test3/haiku T=experiments/test3 K=$HOME/lexsi-backup/judge_keys/test3_haiku_key.jsonl R=$HOME/lexsi-backup/judge_results/test3_haiku
mkdir -p $R
PYTHONPATH=src .venv/bin/python -W ignore -m aemon.evaluation.judging.packets --split heldout3 --report A=$T/A.json \
  --report prompted=$T/prompted.json --report stage1=$T/stage1.json --report haiku=$O/haiku_merged.json \
  --packets $O/packets.jsonl --key $K || exit 1
.venv/bin/python - $O $T <<'PY'
import json, sys
O, T = sys.argv[1:]
old = {json.loads(l)['packet_id'] for l in open(f'{T}/packets.jsonl')}
new = [l for l in open(f'{O}/packets.jsonl') if json.loads(l)['packet_id'] not in old]
open(f'{O}/packets_new.jsonl', 'w').writelines(new)
print(json.dumps({'packets': len(old) + len(new), 'reused': sum(1 for l in open(f'{O}/packets.jsonl')) - len(new), 'new': len(new)}))
PY
judge() {  # backend
  PYTHONPATH=src .venv/bin/python src/aemon/evaluation/judging/judge_v1/run_campaign.py --backend $1 --packets $O/packets_new.jsonl \
    --output $R/$1 --qualification reports/judge/$2 --workers 4 > $O/$1_run.log 2>&1
  echo "$1: $(grep -c '"valid": true' $O/$1_run.log) valid, $(grep -c '"valid": false' $O/$1_run.log) invalid"
}
judge codexsol170 codexsol170_score_qualification.json & judge claudecode claudecode_score_qualification.json & wait
