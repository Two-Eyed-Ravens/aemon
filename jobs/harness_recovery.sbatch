#!/bin/bash
#SBATCH --job-name=harness-recovery
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=%x_%j.log
# Harness recovery selection (DECISIONS 27 November, experiments/harness/recovery_v1): the evaluated adapter merged
# and quantized to Q4_K_M (hash checked), one server slot, then the campaign: three candidates paired with the six-guard
# baseline on 6 training cases, the selected one on the 15 validation cases at 3 attempts. SNAPSHOT is the deployed
# code (with tests/, data/ and experiments/harness/), CODE_REVISION its commit.
set -euo pipefail
L=$HOME/lexsi
: "${SNAPSHOT:?path to the immutable experiment snapshot}"
: "${CODE_REVISION:?source revision label}"
PY=${PY:-$L/env/bin/python}
HF_REPO=CohereLabs/aya-expanse-8b
HF_REV=5062468bf9bc0c6035fd64e06274333ec127d980
EXPECTED_MODEL=5ad8d535d8c94756d8138a9a877cf05987a28cbe82e72322475bfbb12c9b345f
OUT=$L/runs/harness_recovery_v1_$SLURM_JOB_ID
D=/dev/shm/harness-recovery-$SLURM_JOB_ID
PORT=$((20000 + SLURM_JOB_ID % 20000))
SERVER=
cleanup() {
  if [ -n "$SERVER" ]; then
    kill "$SERVER" 2>/dev/null || true
    wait "$SERVER" 2>/dev/null || true
  fi
  rm -rf "$D"
}
trap cleanup EXIT
mkdir "$OUT" "$D"
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
export PYTHONDONTWRITEBYTECODE=1 CODE_REVISION
export PYTHONPATH=$SNAPSHOT/src
export HF_HUB_OFFLINE=0
"$PY" -c 'import jsonschema, pydantic, torch, peft, transformers'
"$PY" - "$HF_REPO" "$HF_REV" "$D/hf" <<'PY'
import sys
from huggingface_hub import snapshot_download
snapshot_download(sys.argv[1], revision=sys.argv[2], local_dir=sys.argv[3],
                  allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])
PY
"$PY" "$SNAPSHOT/scripts/bench/merge_adapter.py" --base "$D/hf" \
  --adapter "$L/runs/base_aya-expanse-8b/adapter" --out "$D/merged"
rm -rf "$D/hf"
PYTHONPATH="$L/llama.cpp/gguf-py:$SNAPSHOT/src" "$PY" "$L/llama.cpp/convert_hf_to_gguf.py" "$D/merged" --outtype bf16 --outfile "$D/model-bf16.gguf"
rm -rf "$D/merged"
"$L/llama.cpp/build/bin/llama-quantize" "$D/model-bf16.gguf" "$D/model-q4.gguf" Q4_K_M
printf '%s  %s\n' "$EXPECTED_MODEL" "$D/model-q4.gguf" | sha256sum -c -
sha256sum "$D/model-q4.gguf" "$L/runs/base_aya-expanse-8b/adapter/adapter_model.safetensors" > "$OUT/weights.sha256"
"$L/llama.cpp/build/bin/llama-server" -m "$D/model-q4.gguf" -ngl 99 -c 8192 --parallel 1 --jinja \
  --reasoning-format none --reasoning-budget 0 --host 127.0.0.1 --port "$PORT" --no-webui > "$OUT/server.log" 2>&1 &
SERVER=$!
ready=0
for attempt in $(seq 1 120); do
  if curl -sf "http://127.0.0.1:$PORT/health" > /dev/null; then
    ready=1
    break
  fi
  kill -0 "$SERVER" || break
  sleep 5
done
[ "$ready" = 1 ] || { tail -20 "$OUT/server.log"; exit 1; }
# The server's identity is recorded once at start; every paired run then refuses a server that differs from it. The
# weights hash was checked by sha256sum above, before the server started.
"$PY" - "http://127.0.0.1:$PORT" "$EXPECTED_MODEL" "$OUT" <<'PY'
import hashlib, json, sys, urllib.request
url, sha, out = sys.argv[1:]
props = json.load(urllib.request.urlopen(url + '/props'))
models = json.load(urllib.request.urlopen(url + '/v1/models'))
expected = {
    'model_path': props['model_path'], 'model_id': models['data'][0]['id'],
    'context': props['default_generation_settings']['n_ctx'], 'build_info': props['build_info'],
    'template_sha256': hashlib.sha256(props['chat_template'].encode()).hexdigest(), 'model_ftype': props['model_ftype'],
    'total_slots': props['total_slots'], 'weights_sha256': sha,
}
receipt = {'model_path': props['model_path'], 'sha256': sha, 'checked_by': 'sha256sum -c in the job before the server started'}
open(f'{out}/runtime-expectation.json', 'w').write(json.dumps(expected, indent=2))
open(f'{out}/runtime-receipt.json', 'w').write(json.dumps(receipt, indent=2))
print(json.dumps(expected))
PY
cd "$SNAPSHOT"
"$PY" -m aemon.evaluation.harness.campaign \
  --protocol experiments/harness/recovery_v1/protocol.json \
  --url "http://127.0.0.1:$PORT" --out "$OUT/results" \
  --expect-runtime "$OUT/runtime-expectation.json" --model-receipt "$OUT/runtime-receipt.json" --model-kind merged \
  --runtime "Aya Expanse 8B merged Q4_K_M $EXPECTED_MODEL context8192 slots1"
echo "Campaign output $OUT"
