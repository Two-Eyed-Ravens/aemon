#!/bin/bash
#SBATCH --job-name=decider
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=%x_%j.log
# The trained decision head for the evidence kind (DECISIONS, 20 November, registered): download the pinned base into
# node memory, train the LoRA and letter head (scripts/decider/train_decider.py), convert the adapter and the base to
# GGUF, serve the base with the adapter, and score the zero-shot base and the trained head on the same items (the 161
# frozen-test items plus the calibration split) with scripts/bench/decision_logits.py. Calibration and the go rule are
# applied afterwards by scripts/decider/report.py. Set NAME, HF_REPO, HF_REV, REVISION; ITEMS_DIR (the uploaded items).
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env/bin/python}
OUT=$L/runs/decider/$NAME
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/decider-$SLURM_JOB_ID
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
mkdir -p $OUT $D/hf
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
echo "node $(hostname), start $(date +%T), code $REVISION, base $HF_REPO@$HF_REV"
for attempt in 1 2 3 4 5 6; do
  HF_HUB_OFFLINE=0 $PY -c "from huggingface_hub import snapshot_download; snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/hf', allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])" && break
  [ $attempt = 6 ] && { echo "download failed"; exit 1; }
  sleep 60
done
echo "downloaded $(date +%T)"
cd $L/code_$REVISION
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 $PY -W ignore scripts/decider/train_decider.py --model $D/hf \
  --items $ITEMS_DIR/train_items.jsonl --calibration $ITEMS_DIR/calibration_items.jsonl --out $OUT
echo "trained $(date +%T)"
$PY $L/llama.cpp/convert_lora_to_gguf.py --base $D/hf --outtype bf16 --outfile $OUT/decider.gguf $OUT/adapter 2>&1 | tail -2
sha256sum $OUT/decider.gguf | tee $OUT/decider.gguf.sha256
G=$D/model-bf16.gguf
PYTHONPATH=$L/llama.cpp/gguf-py $PY $L/llama.cpp/convert_hf_to_gguf.py $D/hf --outtype bf16 --outfile $G 2>&1 | tail -2
rm -f $D/hf/*.safetensors
$L/llama.cpp/build/bin/llama-server -m $G --lora $OUT/decider.gguf -ngl 99 -c 8192 --parallel 1 --jinja --reasoning-format none \
  --reasoning-budget 0 --host 127.0.0.1 --port $PORT --no-webui > $OUT/server.log 2>&1 &
SERVER=$!
for i in $(seq 1 180); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; tail -20 $OUT/server.log; exit 1; }; sleep 5; done
echo "server ready $(date +%T)"
$PY -W ignore scripts/bench/template_check.py --url http://127.0.0.1:$PORT --tokenizer $D/hf --rows $L/rows/final.jsonl || { echo "template check failed"; exit 1; }
(cd scripts/bench && PYTHONPATH=$L/code_$REVISION/src $PY -W ignore decision_logits.py --url http://127.0.0.1:$PORT \
  --items $ITEMS_DIR/offline_items.jsonl --arms base= decider=0 --out $OUT/decision_logits.json | tail -12)
echo "done $(date +%T)"
