#!/bin/bash
#SBATCH --job-name=retention-aya
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=%x_%j.log
# General-capability retention for an Aya Expanse 8B adapter (ablation "general ability", DECISIONS 19 November 20:30):
# the base and the base with the adapter at scale 1, on the same sampled MMLU and ARC-Challenge items as version 1's
# check (reports/retention/), through one server. The base is converted to bf16 in node memory from the pinned weights,
# as in jobs/screen_bases.sbatch. Set NAME, HF_REPO, HF_REV, ADAPTER, REVISION; PY needs transformers.
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env/bin/python}
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
OUT=$L/runs/retention
mkdir -p $OUT
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/retention-$SLURM_JOB_ID
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
mkdir -p $D/hf
for attempt in 1 2 3 4 5 6; do
  HF_HUB_OFFLINE=0 $PY -c "from huggingface_hub import snapshot_download; snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/hf', allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])" && break
  [ $attempt = 6 ] && { echo "download failed"; exit 1; }
  sleep 60
done
G=$D/model-bf16.gguf
PYTHONPATH=$L/llama.cpp/gguf-py $PY $L/llama.cpp/convert_hf_to_gguf.py $D/hf --outtype bf16 --outfile $G 2>&1 | tail -2
rm -rf $D/hf
sha256sum $G $ADAPTER | cut -c1-16,66- | tee $OUT/${NAME}.sha
$L/llama.cpp/build/bin/llama-server -m $G --lora $ADAPTER --lora-init-without-apply -ngl 99 -c 4096 --parallel 1 \
  --jinja --reasoning-format none --host 127.0.0.1 --port $PORT --no-webui > $OUT/${NAME}.server.log 2>&1 &
SERVER=$!
for i in $(seq 1 180); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; tail -5 $OUT/${NAME}.server.log; exit 1; }; sleep 5; done
echo "server ready $(date +%T)"
$L/env/bin/python -W ignore $L/code_$REVISION/scripts/bench/retention.py --url http://127.0.0.1:$PORT \
  --items $L/code_$REVISION/reports/retention/retention_items.jsonl --arms base= adapter=0 --out $OUT/${NAME}.json
echo "done $(date +%T)"
