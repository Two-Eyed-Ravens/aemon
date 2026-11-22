#!/bin/bash
#SBATCH --job-name=screen
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=%x_%j.log
# Model screen (product plan, gate 3, first round): a candidate base model, prompted and not fine-tuned, through the
# unchanged environment on the 15 development cases, 3 attempts each, in two setups: the staged prompt alone (as the
# Tiny Aya base arm ran) and the staged prompt with the final system's decoding guards. The GGUF is downloaded into
# node memory, checked against its sha256, and deleted at the end, so the screen uses no home quota.
# Set NAME, REPO, REV, FILE, SHA, REVISION; LOCAL=path serves a file already on disk instead (the Tiny Aya reference).
# Round 2: ADAPTER=path to a GGUF LoRA serves it on the base, and PROMPT=compact (the format the rows were built in).
# ROUTE=stage route for the adapter (runner --lora-route, such as default=0,conclude=none); ARMS picks the setups.
# CONTEXT=server context in tokens (default 12288; 8192 for Aya Expanse 8B, its trained length).
# HF_REPO and HF_REV instead of REPO/FILE: the base is converted here to a bf16 GGUF from those exact weights, with our
# llama.cpp (as version 1's Tiny Aya file was), and scripts/bench/template_check.py must find the server's tokens for a
# training row identical to training's before any run. PY needs transformers (env_train on the second account).
# ARMS may include decide: the guards plus the decision model on the evidence kind (decide_kind); with an adapter, the
# job first checks that a decision request with the adapter off leaves the next agent request unchanged. Use
# ROUTE=default=0 so every agent request names its adapter. ATTEMPTS sets the attempts (seeds) per case, default 3.
set -euo pipefail
L=$HOME/lexsi
OUT=$L/runs/screen
mkdir -p $OUT
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/screen-$SLURM_JOB_ID
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
CASES=${CASES:-hellberg-base,hellberg-new-evidence-looks,hellberg-new-evidence-comfort,hellberg-new-evidence-favours-looks,hellberg-new-evidence-irrelevant,neumann-base,neumann-new-evidence-irrelevant,jotun-base,jotun-new-evidence-irrelevant,tanita-base,tanita-new-evidence-irrelevant,deere-base,deere-new-evidence-irrelevant,acr-base,acr-new-evidence-irrelevant}
GUARDS=no_repeats,quote_menu,resample_repeats,budget,grounded_beliefs,evidence_first

# The guards less the ones named
without() {
  local out=
  for g in ${GUARDS//,/ }; do
    case " $* " in *" $g "*) ;; *) out=${out:+$out,}$g ;; esac
  done
  echo "$out"
}
# Each arm is one change from the reference "guards" (ablations, DECISIONS 19 November 20:30). Guards that act together
# go together: quote_menu carries evidence_first, and no_repeats and resample_repeats both handle repeats.
arm_args() {
  ARM_RECOVERY=
  ARM_PROMPT=${PROMPT:-staged}
  ARM_ROUTE=${ROUTE:-}
  case $1 in
    staged | none) ;;
    guards) ARM_RECOVERY=$GUARDS ;;
    decide) ARM_RECOVERY=$GUARDS,decide_kind ;;
    minus_quote) ARM_RECOVERY=$(without quote_menu evidence_first) ;;
    minus_repeats) ARM_RECOVERY=$(without no_repeats resample_repeats) ;;
    minus_budget) ARM_RECOVERY=$(without budget) ;;
    minus_ledger) ARM_RECOVERY=$(without grounded_beliefs) ;;
    routed) ARM_RECOVERY=$GUARDS ARM_ROUTE=default=0,position=none,update=none,conclude=none ;;
    staged_prompt) ARM_RECOVERY=$GUARDS ARM_PROMPT=staged ;;
    *) echo "unknown arm $1" && exit 1 ;;
  esac
}
if [ "${DRY:-0}" = 1 ]; then
  for arm in ${ARMS:-staged guards}; do
    arm_args $arm
    echo "$arm: --prompt $ARM_PROMPT ${ARM_RECOVERY:+--recovery $ARM_RECOVERY} ${ARM_ROUTE:+--lora-route $ARM_ROUTE}"
  done
  exit 0
fi
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
echo "node $(hostname), start $(date +%T)"

# PY must have agenttune and auditkit: the runner audits every run with AuditKIT (Nour's env lacks them; use env_train)
PY=${PY:-$L/env/bin/python}
# required tools: stop before any download or GPU work if they cannot be imported (DECISIONS 20 November)
$PY -c "import agenttune, auditkit" || { echo "agenttune or auditkit missing in $PY"; exit 1; }
PRECISION=Q8_0
if [ -n "${LOCAL:-}" ]; then
  G=$LOCAL
elif [ -n "${HF_REPO:-}" ]; then
  mkdir -p $D/hf && G=$D/model-bf16.gguf && PRECISION=bf16
  for attempt in 1 2 3 4 5 6; do
    HF_HUB_OFFLINE=0 $PY -c "from huggingface_hub import snapshot_download; snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/hf', allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', '*.jinja', 'tokenizer*'])" && break
    [ $attempt = 6 ] && { echo "download failed"; exit 1; }
    sleep 60
  done
  PYTHONPATH=$L/llama.cpp/gguf-py $PY $L/llama.cpp/convert_hf_to_gguf.py $D/hf --outtype bf16 --outfile $G 2>&1 | tail -2
  rm -f $D/hf/*.safetensors
else
  mkdir -p $D && G=$D/$FILE
  for attempt in $(seq 1 12); do curl -fsSL -C - -o "$G" "https://huggingface.co/$REPO/resolve/$REV/$FILE" && break; sleep 20; done
  echo "$SHA  $G" | sha256sum -c - || { echo "checksum mismatch"; exit 1; }
fi
WEIGHTS=$(sha256sum $G | cut -d' ' -f1)
echo "serving $NAME, sha256 ${WEIGHTS:0:16}, $(date +%T)"

LORA_ARGS=; [ -n "${ADAPTER:-}" ] && LORA_ARGS="--lora $ADAPTER" && echo "adapter $(sha256sum $ADAPTER | cut -c1-16)"
$L/llama.cpp/build/bin/llama-server -m $G $LORA_ARGS -ngl 99 -c ${CONTEXT:-12288} --parallel 1 --jinja --reasoning-format none --reasoning-budget 0 \
  --host 127.0.0.1 --port $PORT --no-webui > $OUT/${NAME}.server.log 2>&1 &
SERVER=$!
for i in $(seq 1 180); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; tail -20 $OUT/${NAME}.server.log; exit 1; }; sleep 5; done
echo "server ready $(date +%T)"
if [ -n "${HF_REPO:-}" ]; then
  $PY -W ignore $L/code_$REVISION/scripts/bench/template_check.py --url http://127.0.0.1:$PORT --tokenizer $D/hf --rows $L/rows/final.jsonl || { echo "template check failed"; exit 1; }
fi
if [ -n "${ADAPTER:-}" ] && [[ " ${ARMS:-} " == *" decide "* ]]; then
  $PY -W ignore $L/code_$REVISION/scripts/bench/adapter_isolation.py --url http://127.0.0.1:$PORT --rows $L/rows/final.jsonl || { echo "adapter isolation check failed"; exit 1; }
fi

cd $L/code_$REVISION
for arm in ${ARMS:-staged guards}; do
  arm_args $arm
  rm -f $OUT/${NAME}_${arm}.json $OUT/${NAME}_${arm}.episodes.jsonl
  status=0
  PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CODE_REVISION=$REVISION PYTHONPATH=$L/code_$REVISION/src $PY -W ignore \
    -m aemon.agent.run_investigations --require-auditkit --url http://127.0.0.1:$PORT --prompt $ARM_PROMPT --cases "$CASES" --split ${SPLIT:-development} --attempts ${ATTEMPTS:-3} \
    --context ${CONTEXT:-12288} --max-tokens 520 --max-turns 45 ${ARM_RECOVERY:+--recovery $ARM_RECOVERY} ${ARM_ROUTE:+--lora-route $ARM_ROUTE} --model-label "$NAME $PRECISION${ADAPTER:+ + adapter $(basename $(dirname $ADAPTER))}${ARM_ROUTE:+ routed $ARM_ROUTE} (screen, $arm)" \
    --weights-sha256 $WEIGHTS --manifest $OUT/provenance.jsonl --output $OUT/${NAME}_${arm}.json > $OUT/${NAME}_${arm}.log 2>&1 || status=$?
  [ $status = 0 ] || { echo "$NAME $arm: runner exited $status"; tail -5 $OUT/${NAME}_${arm}.log; continue; }
  $L/env/bin/python -c "import json; s=json.load(open('$OUT/${NAME}_${arm}.json'))['summary']; print('$NAME $arm', json.dumps({k: s[k] for k in ('episodes', 'finished', 'stop_reasons', 'refused_calls')}))"
done
# The decision model offline, after the arms (it sets the server's adapter scales): the 161 labelled items, base weights
# and, with an adapter, adapter at scale 1 (reports/decision_logits/, DECISIONS 18 and 19 November)
if [[ " ${ARMS:-} " == *" decide "* ]]; then
  ITEMS=$L/code_$REVISION/reports/decision_logits/decision_items.jsonl
  ADAPTER_ARM=; [ -n "${ADAPTER:-}" ] && ADAPTER_ARM=adapter=0
  (cd $L/code_$REVISION/scripts/bench && PYTHONPATH=$L/code_$REVISION/src $L/env/bin/python -W ignore decision_logits.py --url http://127.0.0.1:$PORT \
    --items $ITEMS --arms base= $ADAPTER_ARM --out $OUT/${NAME}_decision_logits.json | tail -40)
fi
echo "done $(date +%T)"
