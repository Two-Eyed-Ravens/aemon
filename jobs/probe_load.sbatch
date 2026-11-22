#!/bin/bash
#SBATCH --job-name=probe-load
#SBATCH --partition=stud
#SBATCH --qos=stud
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.log
# Before training a new base: does the checkpoint load as a text-only causal LM with every weight in place, what does
# LoRA on all linear layers wrap, and how long are our rows in its tokenizer? CPU only. Set HF_REPO, HF_REV, ROWS;
# PY picks the Python environment (the second account has the training stack in env_train).
set -euo pipefail
L=$HOME/lexsi
D=/dev/shm/probe-$SLURM_JOB_ID
mkdir -p $D
trap 'rm -rf "$D"' EXIT
HF_HUB_OFFLINE=0 ${PY:-$L/env/bin/python} -W ignore - <<PY
from huggingface_hub import snapshot_download
snapshot_download('$HF_REPO', revision='$HF_REV', local_dir='$D/model', allow_patterns=['*.json', '*.safetensors', '*.txt', '*.jinja', 'tokenizer*'])
import json, collections, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
model, info = AutoModelForCausalLM.from_pretrained('$D/model', dtype=torch.bfloat16, output_loading_info=True)
print('class:', type(model).__name__)
for k in ('missing_keys', 'unexpected_keys', 'mismatched_keys'):
    v = list(info.get(k) or [])
    print(k, len(v), collections.Counter('.'.join(x.split('.')[:3]) for x in v).most_common(6))
peft = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules='all-linear', task_type='CAUSAL_LM'))
wrapped = [n for n, _ in peft.named_modules() if n.endswith('lora_A')]
print('lora modules:', len(wrapped), collections.Counter(n.split('.')[-2] for n in wrapped).most_common(10))
peft.print_trainable_parameters()
tok = AutoTokenizer.from_pretrained('$D/model')
rows = [json.loads(l) for l, _ in zip(open('$ROWS'), range(400))]
lens = sorted(len(tok.apply_chat_template(r['messages'][: r['target_index'] + 1], tokenize=True)) for r in rows)
print('row tokens: median', lens[len(lens) // 2], 'max', lens[-1], 'over 8192:', sum(x > 8192 for x in lens), 'of', len(lens))
print('template sample:', repr(tok.apply_chat_template([{'role': 'user', 'content': 'hi'}], tokenize=False, add_generation_prompt=True))[-160:])
PY
