#!/bin/bash
#SBATCH --job-name=llama-tools
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.log
# Builds llama-quantize (CPU only, static) from the llama.cpp release the server was built from, for the inference cost
# bench's 4-bit file, and prints the server's flags for batching, caching and speculative decoding. cmake is installed
# into node memory; only the quantize binary (a few MB) goes to home. Set TAG (the server's build, b12032).
set -euo pipefail
L=$HOME/lexsi
D=/dev/shm/tools-$SLURM_JOB_ID
trap 'rm -rf "$D"' EXIT
mkdir -p $D
python3 -m venv $D/venv && $D/venv/bin/pip install --quiet --no-cache-dir cmake
git clone --quiet --depth 1 --branch ${TAG:-b12032} https://github.com/ggml-org/llama.cpp $D/src
cd $D/src
$D/venv/bin/cmake -S . -B build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release > /dev/null
$D/venv/bin/cmake --build build --target llama-quantize -j 8 > /dev/null
cp build/bin/llama-quantize $L/llama.cpp/build/bin/llama-quantize
$L/llama.cpp/build/bin/llama-quantize --help 2>&1 | grep -m3 -E "Q4_K_M|Q5_K_M|Q8_0"
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
$L/llama.cpp/build/bin/llama-server --help 2>&1 | grep -i -E "spec|draft|lookup|ngram|cache-reuse|cache-type|parallel|cont-batch|kv-unified|flash" | head -40
echo "done $(date +%T)"
