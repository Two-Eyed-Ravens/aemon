#!/bin/bash
#SBATCH --job-name=audit
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.log
# AuditKIT afterwards on saved run reports whose run skipped it (scripts/bench/audit_reports.py), CPU only.
# Set REVISION (code copy) and REPORTS_DIR (the uploaded reports); PY must have agenttune and auditkit.
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env_train/bin/python}
cd $L/code_$REVISION
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 $PY -W ignore scripts/bench/audit_reports.py --split development $REPORTS_DIR/*.json
echo "done $(date +%T)"
