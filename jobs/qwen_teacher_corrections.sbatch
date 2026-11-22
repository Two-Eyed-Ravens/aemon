#!/bin/bash
#SBATCH --job-name=qwen-teacher
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=%x_%j.log
# Second teacher (DECISIONS 19 November 23:43): Qwen3.8-27B (Apache 2.0; Unsloth Q8_0 GGUF, pinned and checked by sha256)
# answers the same student failure states as the Command A+ correction batch, under the same correction protocol
# (aemon.teacher.corrections ask: kept only if the tools accept the call, it repeats nothing and its justification names
# something in the state it acts on) and the same reasoning budget. NO TRAINING. Its answers go to their own output and
# provenance entries, labelled with this teacher. Set STATES (a states file), NAME, REVISION; W slots (default 2).
set -euo pipefail
L=$HOME/lexsi
OUT=$L/runs/teacher
REPO=unsloth/Qwen3.8-27B-GGUF
REV_HF=4af51b3542f775b0a8e4b310bfb3f17e01c306c9
FILE=Qwen3.8-27B-Q8_0.gguf
SHA=a680f44a06920e5d689774823782006aa3acc8db95750323373b24139b67e348
W=${W:-2}
CONTEXT=${CONTEXT:-16384}
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/qwen-$SLURM_JOB_ID
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
mkdir -p $D $OUT
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
echo "node $(hostname), start $(date +%T)"
for attempt in $(seq 1 12); do curl -fsSL -C - -o "$D/$FILE" "https://huggingface.co/$REPO/resolve/$REV_HF/$FILE" && break; sleep 20; done
echo "$SHA  $D/$FILE" | sha256sum -c - || { echo "checksum mismatch"; exit 1; }
$L/llama.cpp/build/bin/llama-server -m $D/$FILE -ngl 99 -c $((CONTEXT * W)) --parallel $W --jinja --reasoning-budget ${THINK:-1024} \
  --host 127.0.0.1 --port $PORT --no-webui > $OUT/$NAME.server.log 2>&1 &
SERVER=$!
for i in $(seq 1 180); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; tail -20 $OUT/$NAME.server.log; exit 1; }; sleep 5; done
echo "server ready $(date +%T)"
cd $L/code_$REVISION
PYTHONPATH=$L/code_$REVISION/src PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CODE_REVISION=$REVISION CHAT_TIMEOUT=1200 $L/env/bin/python -W ignore \
  -m aemon.teacher.corrections ask --states "$STATES" --url http://127.0.0.1:$PORT --workers $W \
  --server-settings "{\"reasoning_budget\": ${THINK:-1024}, \"context_per_slot\": $CONTEXT, \"slots\": $W, \"teacher\": \"qwen3.8-27b Q8_0 $REV_HF\"}" \
  --weights-sha256 $SHA --manifest $OUT/provenance_qwen.jsonl --output $OUT/${NAME}.json > $OUT/${NAME}.log 2>&1
$L/env/bin/python -c "import json; d=json.load(open('$OUT/${NAME}.json')); k=sum(bool(x.get('kept')) for x in d); print(k, 'of', len(d), 'kept')"
echo "done $(date +%T)"
