#!/bin/bash
#SBATCH --job-name=export-gguf
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --gres=gpu:4g.40gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --output=%x_%j.log
# Publish the 4-bit model that was evaluated (DECISIONS 27 November). The same steps as jobs/inference_bench.sbatch:
# the base at a pinned revision, the adapter merged, converted to bf16 GGUF and quantized to Q4_K_M, all in node memory.
# The file must hash to the evaluated weights (EXPECT_SHA256) or nothing is uploaded; then it goes to HF_TARGET.
# Set HF_REPO, HF_REV, ADAPTER_DIR, REVISION, EXPECT_SHA256, HF_TARGET; optional PY.
set -euo pipefail
L=$HOME/lexsi
PY=${PY:-$L/env/bin/python}
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load cuda/12.8
OUT=$L/runs/export_gguf
mkdir -p $OUT
D=/dev/shm/export-$SLURM_JOB_ID
trap 'rm -rf "$D"' EXIT
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
rm -rf $D/merged
$L/llama.cpp/build/bin/llama-quantize $D/m-bf16.gguf $D/aemon-8b-Q4_K_M.gguf Q4_K_M 2>&1 | tail -1
got=$(sha256sum $D/aemon-8b-Q4_K_M.gguf | cut -d' ' -f1)
echo "sha256 $got" | tee $OUT/weights.sha
ls -la $D/*.gguf | tee $OUT/sizes.txt
[ "$got" = "$EXPECT_SHA256" ] || { echo "hash differs from the evaluated weights: not uploading"; exit 1; }
rm -f $D/m-bf16.gguf
HF_HUB_OFFLINE=0 $PY -c "
from huggingface_hub import HfApi
HfApi().upload_file(path_or_fileobj='$D/aemon-8b-Q4_K_M.gguf', path_in_repo='aemon-8b-Q4_K_M.gguf', repo_id='$HF_TARGET', commit_message='Q4_K_M weights, sha256 $got')
print('uploaded')"
echo "done $(date +%T)"
