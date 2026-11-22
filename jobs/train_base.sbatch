#!/bin/bash
#SBATCH --job-name=train-base
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=96G
#SBATCH --time=23:30:00
#SBATCH --output=%x_%j.log
# Model screen round 2 (product plan, gate 3): version 1's recipe on a commercially licensed base. The same Command A+
# rows (the only teacher data cleared for commercial training) and corrections, the same LoRA, schedule, validation
# companies and seed as runs/final_pilot, plus gradient checkpointing so a 7 to 12B model fits one GPU. The base's
# weights are downloaded into node memory and deleted at the end; only the adapter and its report stay in home.
# Then the adapter is converted to GGUF against the same base, and the screen job evaluates it (jobs/screen_bases.sbatch).
# Set NAME, HF_REPO, HF_REV, REVISION; MINUTES to stop and save early; MAX_STEPS for a smoke run; CHAT_KWARGS as JSON,
# such as {"enable_thinking": false} for Qwen3.5. GC=0 trains without gradient checkpointing (faster, more memory; the run
# resumes from its last checkpoint, so an out-of-memory stop is resubmitted with GC=1). PY picks the Python environment.
# ROWS replaces the teacher rows file (the training-data experiment's composition condition).
# EXTRA_SHARE caps the extra rows' share of target tokens (default 0.2; 0 trains on the teacher rows alone).
# SEED sets the training seed (default 7, version 1's), for repeat runs that measure seed-to-seed spread.
# EXTRAS=path replaces the correction rows as the extra rows (round 3b: corrections plus recovery rows).
# UNSLOTH=1 builds the model and LoRA with Unsloth (its environment from jobs/env_unsloth.sbatch, its standard gradient
# checkpointing): 4.3 times faster per step on Qwen3.5-4B with matching losses (DECISIONS, 19 November).
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env/bin/python}
CHECKPOINTING=; [ "${GC:-1}" = 1 ] && CHECKPOINTING=--gradient-checkpointing
UNSLOTH_ARGS=
if [ "${UNSLOTH:-0}" = 1 ]; then
  PY=$L/env_unsloth/bin/python
  export AEMON_UNSLOTH=1 AEMON_UNSLOTH_CHECKPOINTING=true
  UNSLOTH_ARGS=--unsloth
  CHECKPOINTING=
fi
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
OUT=$L/runs/base_$NAME
D=/dev/shm/train-$SLURM_JOB_ID
mkdir -p $OUT $D
trap 'rm -rf "$D"' EXIT
echo "node $(hostname), start $(date +%T), gradient checkpointing ${GC:-1}, unsloth ${UNSLOTH:-0}"
# The Hub sometimes refuses a request (HTTP 499 on 19 November); the download resumes, so retry a few times
for attempt in 1 2 3 4 5 6; do
  HF_HUB_OFFLINE=0 $PY -c "
from huggingface_hub import snapshot_download
snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/model', allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])
print('downloaded')" && break
  [ $attempt = 6 ] && { echo "download failed"; exit 1; }
  sleep 60
done
cd $L/code_$REVISION
export PYTHONPATH=$L/code_$REVISION/src PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CODE_REVISION=$REVISION
$PY -W ignore -m aemon.training.train --model $D/model --rows ${ROWS:-$L/rows/final.jsonl} --out $OUT \
  ${MAX_STEPS:+--max-steps $MAX_STEPS} --epochs 2 --warmup 0.05 --save-steps 50 --learning-rate 1e-4 --batch 1 --accumulate 4 --max-length 8192 --seed ${SEED:-7} \
  --minutes ${MINUTES:-1300} --validation-cases hellberg neumann jotun tanita deere acr --validation-rows-per-company 40 \
  --extra-rows ${EXTRAS:-$L/rows/final_corrections.jsonl} --extra-token-share ${EXTRA_SHARE:-0.2} $CHECKPOINTING $UNSLOTH_ARGS --eval-batch 1 --chat-template-kwargs "${CHAT_KWARGS:-{\}}"
echo "trained $(date +%T)"
export PYTHONPATH=$L/llama.cpp/gguf-py
$PY $L/llama.cpp/convert_lora_to_gguf.py --base $D/model --outtype bf16 --outfile $OUT/adapter.gguf $OUT/adapter 2>&1 | tail -3
sha256sum $OUT/adapter.gguf | tee $OUT/adapter.gguf.sha256
echo "done $(date +%T)"
