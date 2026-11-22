# aemon-8b as a hosted demo on one L4 GPU: the React interface, the FastAPI app and llama.cpp serving Aya Expanse 8B
# with adapter A (Stage 2's evaluated configuration), in one container (port 7860, user 1000).
FROM node:22-slim AS web
WORKDIR /web
COPY app/web/package.json app/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY app/web ./
RUN npm run build

# llama.cpp's official prebuilt CUDA server (llama-server plus its shared libraries in /app), pinned by digest. Compiling
# it in the Space ran the builder out of memory or past its 30-minute limit, and the one binary that did build never
# began serving. The evaluated runs used release b12032; this demo uses a newer llama.cpp with the same model and adapter.
FROM ghcr.io/ggml-org/llama.cpp:server-cuda@sha256:f46a7938f84a62f7c2eba2dfc985d921cb54fb3ec7b4e729cec2cee2cbace609 AS llama

FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=llama /app/ /opt/llama/
ENV LD_LIBRARY_PATH=/opt/llama:/usr/local/nvidia/lib64:/usr/local/nvidia/lib
COPY app/requirements-app.txt /tmp/requirements-app.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements-app.txt huggingface_hub==1.33.0
# Aya Expanse 8B (CohereLabs, CC-BY-NC 4.0) at 8 bits, a fixed revision of bartowski's conversion; the evaluated runs
# used a bf16 conversion of the same weights, and the inference bench found 4-bit finished as many runs
# A plain streamed download, checked by sha256: the Hub client's transfer backend ran the builder out of memory (137)
RUN mkdir -p /opt/model && curl -fsSL --retry 5 -o /opt/model/aya-expanse-8b-Q8_0.gguf \
      https://huggingface.co/bartowski/aya-expanse-8b-GGUF/resolve/f9d62ed0c58e6f2ae17975df990b1b8a4013b596/aya-expanse-8b-Q8_0.gguf \
    && echo "75e5bfef4bee065bf07903ad941cac35a2809ecd84baba098f5307645655c22d  /opt/model/aya-expanse-8b-Q8_0.gguf" | sha256sum -c -
RUN id -u 1000 >/dev/null 2>&1 || useradd -m -u 1000 user
WORKDIR /home/aemon
COPY --chown=1000:1000 . .
COPY --chown=1000:1000 --from=web /web/dist app/web/dist
RUN chmod +x start.sh && chown 1000:1000 /home/aemon
USER 1000
ENV HOME=/home/aemon AEMON_SEED=/home/aemon/seed/history.json LEXSI_DATA=/tmp/aemon-data LIVE_MODEL=aemon8b \
    MAX_TURNS=45 PYTHONDONTWRITEBYTECODE=1 CROSS_SITE_COOKIE=1
EXPOSE 7860
CMD ["./start.sh"]
