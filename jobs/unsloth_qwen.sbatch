#!/bin/bash
#SBATCH --job-name=unsloth-qwen
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=%x_%j.log
# Unsloth on a round-2 base (the 2026-11-11 fair test was on Tiny Aya): the same rows, LoRA (rank 16, alpha 32, every
# linear layer including Qwen3.5's linear-attention projections), seed, chat-template options and steps, once through
# the current trainer and once with the model and LoRA built by Unsloth, both with standard gradient checkpointing.
# Reported: losses, median seconds per step after step 10, peak memory, LoRA layer count, and GGUF conversion.
# Unsloth gets its own environment ($L/env_unsloth, the newest release that works with the project's torch 2.11 for
# CUDA 12.8, versions printed). Set HF_REPO, HF_REV, REVISION.
set -euo pipefail
set -x
L=$HOME/lexsi
OUT=$L/runs/unsloth_qwen
D=/dev/shm/unsloth-$SLURM_JOB_ID
mkdir -p $OUT $D
trap 'rm -rf "$D"' EXIT
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
CODE=$L/code_$REVISION
if [ ! -f $L/env_unsloth/.installed ]; then
  rm -rf $L/env_unsloth
  ${PY:-$L/env/bin/python} -m venv $L/env_unsloth
  $L/env_unsloth/bin/pip install --no-cache-dir -q --upgrade pip
  $L/env_unsloth/bin/pip install --no-cache-dir --prefer-binary --extra-index-url https://download.pytorch.org/whl/cu128 "torch==2.11.0+cu128" unsloth datasets tenacity scipy jsonschema python-dotenv tabulate > $OUT/pip.log 2>&1 \
    || { echo "install failed"; grep -iE "error|conflict|no matching" $OUT/pip.log | tail -20 | cut -c1-240; exit 1; }
  $L/env_unsloth/bin/pip install --no-cache-dir -q --no-deps \
    "agenttune @ git+https://github.com/Lexsi-Labs/AgentTune@d4db4c12d52342227c4113a70183d0f64aa2f345" \
    "auditkit @ git+https://github.com/Lexsi-Labs/AuditKIT@71316da345784ff220d5ed59337441a59ab31526" > $OUT/pip_lexsi.log 2>&1
  touch $L/env_unsloth/.installed
fi
$L/env_unsloth/bin/python -c "import torch, transformers, trl, peft, unsloth; print('unsloth env', torch.__version__, transformers.__version__, trl.__version__, peft.__version__, unsloth.__version__)"
for attempt in 1 2 3 4 5 6; do HF_HUB_OFFLINE=0 $L/env_unsloth/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/model', allow_patterns=['*.json', '*.safetensors', '*.txt', '*.jinja', 'tokenizer*'])" && break; [ $attempt = 6 ] && exit 1; sleep 60; done
export PYTHONPATH=$CODE/src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
head -n ${N_ROWS:-160} $L/rows/final.jsonl > $OUT/rows.jsonl
COMMON="--model $D/model --rows $OUT/rows.jsonl --max-steps ${STEPS:-30} --batch 1 --accumulate 4 --max-length 8192 --save-steps 1000 --seed 7 --minutes 100 --chat-template-kwargs {\"enable_thinking\":false}"
run() {  # name, python, extra
  local T0=$(date +%s)
  rm -rf $OUT/$1
  cd $CODE && $2 -W ignore -m aemon.training.train $COMMON --out $OUT/$1 $3 > $OUT/$1.log 2>&1 || { echo "$1 failed"; tail -15 $OUT/$1.log | cut -c1-200; return 1; }
  echo "$1 done in $(( $(date +%s) - T0 )) s"
}
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
run current ${PY:-$L/env/bin/python} "--gradient-checkpointing" || true
AEMON_UNSLOTH=1 AEMON_UNSLOTH_CHECKPOINTING=true run unsloth $L/env_unsloth/bin/python "--unsloth" || true
${PY:-$L/env/bin/python} - $OUT <<'PY'
import glob, json, sys
out = sys.argv[1]
for name in ('current', 'unsloth'):
    reports = sorted(glob.glob(f'{out}/{name}/report-step*.json'))
    if not reports:
        print(name, 'no report')
        continue
    r = json.load(open(reports[-1]))
    steady = sorted(r.get('step_seconds', [])[10:])
    median = steady[len(steady) // 2] if steady else None
    losses = r.get('losses') or []
    print(name, json.dumps({'losses_first_last': losses[:3] + losses[-3:], 'median_step_seconds_after_10': median, 'peak_gpu_gb': r.get('peak_gpu_gb'), 'steps': r.get('global_step')}))
PY
grep -h -i -E "trainable params|lora" $OUT/unsloth.log | head -4 | cut -c1-200
for name in current unsloth; do
  [ -d $OUT/$name/adapter ] || continue
  PYTHONPATH=$L/llama.cpp/gguf-py ${PY:-$L/env/bin/python} $L/llama.cpp/convert_lora_to_gguf.py --base $D/model --outtype bf16 --outfile $OUT/$name.gguf $OUT/$name/adapter 2>&1 | tail -1 | cut -c1-160
done
echo "done $(date +%T)"
