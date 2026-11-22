#!/usr/bin/env bash
# Starts llama.cpp on the GPU (Aya Expanse 8B, adapter A loaded but applied per request) and the app on port 7860.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export CODE_REVISION="$(cat REVISION 2>/dev/null || echo unknown)"
/opt/llama/llama-server -m /opt/model/aya-expanse-8b-Q8_0.gguf --lora adapters/aemon-8b-adapter.gguf --lora-init-without-apply \
  -ngl 99 -c 16384 --parallel 2 --jinja --reasoning-format none --host 127.0.0.1 --port 8091 --no-webui \
  2>&1 | sed -u 's/^/[llama] /' &
echo "aemon-8b demo: model server starting on the GPU, app on port ${PORT:-7860}"
exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port "${PORT:-7860}" --app-dir app --log-level info --proxy-headers --forwarded-allow-ips "*"
