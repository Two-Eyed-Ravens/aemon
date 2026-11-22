#!/bin/bash
#SBATCH --job-name=env-train
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=%x_%j.log
# The training environment on an account that has only the serving one: a venv from the same Python with the project's
# locked requirements (requirements.lock.txt), at $L/env_train. Built on a compute node; the marker is written only
# after a complete install. Set REVISION (the code copy holding the lock file).
set -euo pipefail
L=$HOME/lexsi
E=$L/env_train
[ -f $E/.installed ] && { echo "already installed"; exit 0; }
rm -rf $E
$L/env/bin/python -m venv $E
$E/bin/pip install --no-cache-dir -q --upgrade pip
$E/bin/pip install --no-cache-dir -q --prefer-binary --extra-index-url https://download.pytorch.org/whl/cu128 -r $L/code_$REVISION/requirements.lock.txt > $L/env_train_pip.log 2>&1 \
  || { echo "install failed"; grep -iE "error|conflict|no matching" $L/env_train_pip.log | tail -20 | cut -c1-240; exit 1; }
$E/bin/python -c "import torch, transformers, peft, trl, agenttune; print('env_train', torch.__version__, transformers.__version__, peft.__version__, trl.__version__)"
touch $E/.installed
df -h $HOME | tail -1
