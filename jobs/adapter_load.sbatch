#!/bin/bash
#SBATCH --job-name=adapter-load
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:3g.40gb:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:40:00
#SBATCH --output=%x_%j.log
# Does llama.cpp load this GGUF LoRA on this base, and does applying it change the output? One prompt, adapter at scale
# 0 and 1. Set REPO, REV, FILE, SHA, ADAPTER.
set -euo pipefail
L=$HOME/lexsi
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
PORT=$((20000 + SLURM_JOB_ID % 20000))
D=/dev/shm/load-$SLURM_JOB_ID
mkdir -p $D
SERVER=
trap '[ -n "$SERVER" ] && kill $SERVER 2>/dev/null || true; rm -rf "$D"' EXIT
curl -fsSL -o $D/$FILE "https://huggingface.co/$REPO/resolve/$REV/$FILE"
echo "$SHA  $D/$FILE" | sha256sum -c -
$L/llama.cpp/build/bin/llama-server -m $D/$FILE --lora $ADAPTER --lora-init-without-apply -ngl 99 -c 4096 --jinja \
  --reasoning-format none --reasoning-budget 0 --host 127.0.0.1 --port $PORT --no-webui > $L/bench/adapter-load_$SLURM_JOB_ID.server.log 2>&1 &
SERVER=$!
for i in $(seq 1 120); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; kill -0 $SERVER || { echo "server died"; grep -i -E "lora|error|fail" $L/bench/adapter-load_$SLURM_JOB_ID.server.log | tail -10; exit 1; }; sleep 5; done
grep -i -E "lora|adapter" $L/bench/adapter-load_$SLURM_JOB_ID.server.log | tail -6 || echo "no lora line in the server log"
echo "adapters: $(curl -s http://127.0.0.1:$PORT/lora-adapters)"
# Greedy text can match when a weak adapter shifts probabilities only a little, so compare the first tokens' log-probabilities
for scale in 0 1; do
  curl -s http://127.0.0.1:$PORT/lora-adapters -H 'Content-Type: application/json' -d "[{\"id\": 0, \"scale\": $scale}]" > /dev/null
  curl -s http://127.0.0.1:$PORT/v1/chat/completions -H 'Content-Type: application/json' \
    -d '{"messages": [{"role": "user", "content": "Name the first tool an analyst should call to read a case brief. Reply with JSON."}], "max_tokens": 12, "temperature": 0, "logprobs": true, "top_logprobs": 3, "chat_template_kwargs": {"enable_thinking": false}}' \
    > $D/scale$scale.json
  $L/env/bin/python -c "import json; c=json.load(open('$D/scale$scale.json'))['choices'][0]; print('scale $scale:', repr(c['message']['content'][:80])); print('  logprobs:', [round(t['logprob'], 5) for t in c['logprobs']['content']])"
done
$L/env/bin/python -c "
import json
a, b = (json.load(open(f'$D/scale{s}.json'))['choices'][0]['logprobs']['content'] for s in (0, 1))
diff = max(abs(x['logprob'] - y['logprob']) for x, y in zip(a, b))
print('largest log-probability change from the adapter:', diff, '(applied)' if diff > 1e-4 else '(no effect: not applied, or too weak to measure)')"
echo "load test done"
