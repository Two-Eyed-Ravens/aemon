#!/bin/bash
# Haiku arm on test set 3, read as registered: each judge's predictions for the three arms and for Haiku's new packets
# are joined, then scripts/test3/analyze.py (unchanged) reports Haiku minus A and Haiku minus the Stage 1 system.
set -euo pipefail
cd "$(dirname "$0")/../../.."
O=experiments/test3/haiku T=experiments/test3 R=$HOME/lexsi-backup/judge_results/test3_haiku
mkdir -p $O/judging
cp $HOME/lexsi-backup/judge_keys/test3_haiku_key.jsonl $O/test3_haiku_key.jsonl
for j in codexsol170 claudecode; do
  cat $T/judging/${j}_predictions.jsonl $R/$j/predictions.jsonl > $O/judging/${j}_predictions.jsonl
done
PYTHONPATH=src .venv/bin/python scripts/test3/analyze.py --key $O/test3_haiku_key.jsonl \
  --judge codexsol170=$O/judging/codexsol170_predictions.jsonl --judge claudecode=$O/judging/claudecode_predictions.jsonl \
  --compare haiku,A --compare haiku,stage1 --out $O/report.json > /dev/null
echo "report: $O/report.json"
