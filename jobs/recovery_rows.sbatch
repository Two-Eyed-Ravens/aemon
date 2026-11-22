#!/bin/bash
#SBATCH --job-name=recovery-rows
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.log
# Round 3b data: recovery rows built by rule from the teacher episodes already in the training rows
# (src/aemon/rows/recovery_rows.py), then joined with the existing correction rows into one extras file for
# jobs/train_base.sbatch. CPU only. Set REVISION; the teacher reports and their manifest are in $L/teacher_reports,
# with used.txt naming the 52 reports rows/final.jsonl was built from (rows/final.decisions.json).
set -euo pipefail
L=$HOME/lexsi
R=$L/teacher_reports
cd $L/code_$REVISION
export PYTHONPATH=$L/code_$REVISION/src PYTHONDONTWRITEBYTECODE=1
OUT=$L/rows/recovery_$REVISION.jsonl
$L/env/bin/python -W ignore -m aemon.rows.recovery_rows --reports $(sed "s|^|$R/|" $R/used.txt) \
  --training-rows $L/rows/final.jsonl --manifest $R/provenance.jsonl --per-episode 2 --output $OUT
cat $L/rows/final_corrections.jsonl $OUT > $L/rows/extras_$REVISION.jsonl
wc -l $OUT $L/rows/extras_$REVISION.jsonl
sha256sum $OUT $L/rows/extras_$REVISION.jsonl
echo "done $(date +%T)"
