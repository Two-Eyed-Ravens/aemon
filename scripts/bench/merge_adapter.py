"""Merge a PEFT LoRA adapter into its base weights and save the result as one Hugging Face model, so it can be converted
and quantized like any base and served without a LoRA pass per token (inference cost bench, DECISIONS 19 November).

Usage: python merge_adapter.py --base HF_DIR --adapter ADAPTER_DIR --out OUT_DIR
"""

import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--adapter', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    base = AutoModelForCausalLM.from_pretrained(args.base, dtype=torch.bfloat16)
    merged = PeftModel.from_pretrained(base, args.adapter).merge_and_unload()
    merged.save_pretrained(args.out, safe_serialization=True)
    AutoTokenizer.from_pretrained(args.base).save_pretrained(args.out)
    print('merged', type(merged).__name__, sum(p.numel() for p in merged.parameters()))


if __name__ == '__main__':
    main()
