#!/bin/bash
#SBATCH --job-name=decision-base
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:3g.40gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=%x_%j.log
# The decision-model measurement (scripts/bench/decision_logits.py) on a candidate base: its Q8_0 GGUF downloaded into
# node memory and checked by sha256, no adapter. Set NAME, REPO, REV, FILE, SHA.
set -euo pipefail
L=$HOME/lexsi
B=$L/bench
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/decision-$SLURM_JOB_ID
mkdir -p $D
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
G=$D/$FILE
for attempt in $(seq 1 12); do curl -fsSL -C - -o "$G" "https://huggingface.co/$REPO/resolve/$REV/$FILE" && break; sleep 20; done
echo "$SHA  $G" | sha256sum -c -
$L/llama.cpp/build/bin/llama-server -m $G -ngl 99 -c 8192 --parallel 1 --jinja --reasoning-format none --reasoning-budget 0 \
  --host 127.0.0.1 --port $PORT --no-webui > $B/decision_${NAME}.server.log 2>&1 &
SERVER=$!
for i in $(seq 1 120); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; exit 1; }; sleep 5; done
$L/env/bin/python -W ignore $B/decision_logits.py --url http://127.0.0.1:$PORT --items $B/decision_items.jsonl --arms base= --out $B/decision_${NAME}.json
echo "done $(date +%T)"
