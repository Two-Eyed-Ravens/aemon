# aemon-8b as a hosted demo on one L4 GPU: the React interface, the FastAPI app and llama.cpp serving Aya Expanse 8B
# with adapter A (Stage 2's evaluated configuration), in one container (port 7860, user 1000).
FROM node:22-slim AS web
WORKDIR /web
COPY app/web/package.json app/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY app/web ./
RUN npm run build

# llama.cpp b12032, the release every evaluated run used, compiled for the L4 (compute capability 8.9); two compile
# jobs, since eight ran the build machine out of memory (exit 137)
FROM nvidia/cuda:12.6.3-devel-ubuntu24.04 AS llama
RUN apt-get update && apt-get install -y --no-install-recommends git cmake build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch b12032 https://github.com/ggml-org/llama.cpp /src \
    && cmake -S /src -B /build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="75;86;89" -DBUILD_SHARED_LIBS=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
       -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_SERVER=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /build --target llama-server -j 2

FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=llama /build/bin/llama-server /opt/llama/llama-server
COPY app/requirements-app.txt /tmp/requirements-app.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements-app.txt huggingface_hub==1.33.0
# Aya Expanse 8B (CohereLabs, CC-BY-NC 4.0) at 8 bits, a fixed revision of bartowski's conversion; the evaluated runs
# used a bf16 conversion of the same weights, and the inference bench found 4-bit finished as many runs
RUN /opt/venv/bin/python -c "from huggingface_hub import hf_hub_download; hf_hub_download('bartowski/aya-expanse-8b-GGUF', 'aya-expanse-8b-Q8_0.gguf', revision='f9d62ed0c58e6f2ae17975df990b1b8a4013b596', local_dir='/opt/model')" \
    && rm -rf /opt/model/.cache
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
