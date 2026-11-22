#!/bin/bash
#SBATCH --job-name=env-unsloth
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=%x_%j.log
# The Unsloth environment ($L/env_unsloth) alone, as jobs/unsloth_qwen.sbatch builds it: Unsloth's newest release that
# works with the project's torch 2.11 for CUDA 12.8, plus AgentTune and AuditKIT at the locked commits.
set -euo pipefail
L=$HOME/lexsi
OUT=$L/runs/env_unsloth
mkdir -p $OUT
if [ ! -f $L/env_unsloth/.installed ]; then
  rm -rf $L/env_unsloth
  $L/env/bin/python -m venv $L/env_unsloth
  $L/env_unsloth/bin/pip install --no-cache-dir -q --upgrade pip
  $L/env_unsloth/bin/pip install --no-cache-dir --prefer-binary --extra-index-url https://download.pytorch.org/whl/cu128 "torch==2.11.0+cu128" "unsloth==2026.11.6" datasets tenacity scipy jsonschema python-dotenv tabulate > $OUT/pip.log 2>&1 \
    || { echo "install failed"; grep -iE "error|conflict|no matching" $OUT/pip.log | tail -20 | cut -c1-240; exit 1; }
  $L/env_unsloth/bin/pip install --no-cache-dir -q --no-deps \
    "agenttune @ git+https://github.com/Lexsi-Labs/AgentTune@d4db4c12d52342227c4113a70183d0f64aa2f345" \
    "auditkit @ git+https://github.com/Lexsi-Labs/AuditKIT@71316da345784ff220d5ed59337441a59ab31526" > $OUT/pip_lexsi.log 2>&1
  touch $L/env_unsloth/.installed
fi
# Unsloth refuses to import without a GPU, and this job runs on a CPU node, so the check reads its installed version
$L/env_unsloth/bin/python -c "import importlib.metadata as m, torch, transformers, trl, peft; print('unsloth env', torch.__version__, transformers.__version__, trl.__version__, peft.__version__, m.version('unsloth'))"
