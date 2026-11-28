#!/bin/bash
#SBATCH --job-name=inference-bench
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=10:00:00
#SBATCH --output=%x_%j.log
# Inference cost bench (DECISIONS 19 November): can the fine-tuned agent cost less per investigation than Claude Haiku
# 5.5? The adapter is merged into the base weights (no LoRA pass per token), converted to bf16 and 8-bit GGUF and
# quantized to 4-bit (Q4_K_M, jobs/llama_tools.sbatch builds the quantizer), all in node memory. Each precision is
# served with 1, 4, 8 and 16 investigations at once (continuous batching; the server keeps each slot's previous prompt
# cached, and the share of prompt tokens it did not recompute is recorded), on the 15 development cases with the guards
# and the compact prompt: 1 attempt per case at 1 slot, 3 above, so the slots have work. Wall time gives investigations
# per GPU hour; scripts/bench/inference_summary.py turns that into cost per investigation. Set NAME, HF_REPO, HF_REV,
# ADAPTER_DIR (the PEFT adapter), REVISION, PY (transformers and peft: env_train on the second account).
# Optional: PRECISIONS, SLOTS, CASES, SPLIT (default development) and ATTEMPTS (default 3, 1 at one slot).
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env/bin/python}
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
OUT=$L/runs/bench_$NAME
mkdir -p $OUT
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/bench-$SLURM_JOB_ID
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
CASES=${CASES:-hellberg-base,hellberg-new-evidence-looks,hellberg-new-evidence-comfort,hellberg-new-evidence-favours-looks,hellberg-new-evidence-irrelevant,neumann-base,neumann-new-evidence-irrelevant,jotun-base,jotun-new-evidence-irrelevant,tanita-base,tanita-new-evidence-irrelevant,deere-base,deere-new-evidence-irrelevant,acr-base,acr-new-evidence-irrelevant}
GUARDS=no_repeats,quote_menu,resample_repeats,budget,grounded_beliefs,evidence_first
echo "node $(hostname), start $(date +%T)"

mkdir -p $D/hf
for attempt in 1 2 3 4 5 6; do
  HF_HUB_OFFLINE=0 $PY -c "from huggingface_hub import snapshot_download; snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/hf', allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])" && break
  [ $attempt = 6 ] && { echo "download failed"; exit 1; }
  sleep 60
done
$PY -W ignore $L/code_$REVISION/scripts/bench/merge_adapter.py --base $D/hf --adapter $ADAPTER_DIR --out $D/merged
rm -rf $D/hf
export PYTHONPATH=$L/llama.cpp/gguf-py
$PY $L/llama.cpp/convert_hf_to_gguf.py $D/merged --outtype bf16 --outfile $D/m-bf16.gguf 2>&1 | tail -1
$PY $L/llama.cpp/convert_hf_to_gguf.py $D/merged --outtype q8_0 --outfile $D/m-q8_0.gguf 2>&1 | tail -1
rm -rf $D/merged
$L/llama.cpp/build/bin/llama-quantize $D/m-bf16.gguf $D/m-q4_k_m.gguf Q4_K_M 2>&1 | tail -1
unset PYTHONPATH
sha256sum $D/m-*.gguf | cut -c1-16,66- | tee $OUT/weights.sha
ls -la $D/m-*.gguf

TIMINGS=$OUT/timings.jsonl
for precision in ${PRECISIONS:-bf16 q8_0 q4_k_m}; do
  for slots in ${SLOTS:-1 4 8 16}; do
    attempts=${ATTEMPTS:-3}
    [ -z "${ATTEMPTS:-}" ] && [ $slots = 1 ] && attempts=1
    tag=${precision}_s${slots}
    rm -f $OUT/$tag.json $OUT/$tag.episodes.jsonl
    $L/llama.cpp/build/bin/llama-server -m $D/m-$precision.gguf -ngl 99 -c $((8192 * slots)) --parallel $slots --jinja \
      --reasoning-format none --reasoning-budget 0 --host 127.0.0.1 --port $PORT --no-webui > $OUT/$tag.server.log 2>&1 &
    SERVER=$!
    ready=0
    for i in $(seq 1 180); do
      curl -sf http://127.0.0.1:$PORT/health > /dev/null && ready=1 && break
      kill -0 $SERVER 2>/dev/null || break
      sleep 5
    done
    if [ $ready = 0 ]; then
      echo "$tag: server did not start"
      tail -3 $OUT/$tag.server.log
      kill $SERVER 2>/dev/null || true
      SERVER=
      continue
    fi
    started=$(date +%s)
    status=0
    (cd $L/code_$REVISION && PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CODE_REVISION=$REVISION PYTHONPATH=$L/code_$REVISION/src \
      $L/env/bin/python -W ignore -m aemon.agent.run_investigations --url http://127.0.0.1:$PORT --prompt compact --split ${SPLIT:-development} --cases "$CASES" \
      --attempts $attempts --workers $slots --context 8192 --max-tokens 520 --max-turns 45 --recovery $GUARDS \
      --model-label "$NAME merged $precision, $slots at once (bench)" --weights-sha256 $(sha256sum $D/m-$precision.gguf | cut -d' ' -f1) \
      --manifest $OUT/provenance.jsonl --output $OUT/$tag.json > $OUT/$tag.log 2>&1) || status=$?
    wall=$(($(date +%s) - started))
    kill $SERVER 2>/dev/null || true
    wait $SERVER 2>/dev/null || true
    SERVER=
    if [ $status != 0 ]; then
      echo "$tag: runner exited $status"
      tail -3 $OUT/$tag.log
      continue
    fi
    echo "{\"precision\": \"$precision\", \"slots\": $slots, \"wall_seconds\": $wall, \"report\": \"$OUT/$tag.json\"}" >> $TIMINGS
    echo "$tag: $(date +%T), $wall s"
  done
done
PYTHONPATH=$L/code_$REVISION/src $L/env/bin/python $L/code_$REVISION/scripts/bench/inference_summary.py --timings $TIMINGS --out $OUT/summary.json
echo "done $(date +%T)"
