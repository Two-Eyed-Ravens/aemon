---
license: cc-by-nc-4.0
base_model: two-eyed-ravens/aemon-8b
library_name: gguf
language:
- en
tags:
- agentic
- tool-use
- strategy
- gguf
- llama.cpp
- quantized
pipeline_tag: text-generation
---

# aemon-8b GGUF: the strategy-investigation agent in one 5 GB file

*weigh what is known. test what is not.*

Team Two-eyed Ravens (Hatem Saadallah, Nour Jennane), Lexsi AI Hackathon, Track 3 (Agentic Fine-Tuning), Stage 2.
The adapter and its full evaluation: [two-eyed-ravens/aemon-8b](https://huggingface.co/two-eyed-ravens/aemon-8b). Code,
harness and paper: [github.com/Two-Eyed-Ravens/aemon](https://github.com/Two-Eyed-Ravens/aemon).

[aemon-8b](https://huggingface.co/two-eyed-ravens/aemon-8b) is a LoRA adapter for Aya Expanse 8B that runs a structured
strategy investigation through twelve guarded tools. This repository holds the same model merged into its base and
quantized to 4 bits, so it needs no separate base download, no LoRA pass and no data-centre GPU.

| | This file (Q4_K_M) | Full precision (bf16) |
|---|---|---|
| Size | **5.06 GB** | 16.07 GB |
| Investigations per GPU hour, one at a time | **65.8** | 32.3 |
| Investigations per GPU hour, 8 at once | **93.8** | 56.8 |
| Cost per investigation, 8 at once, at $1.76 per A100 hour | **$0.019** | $0.031 |
| Blind quality on 12 unseen companies (0–3) | 1.59 | 1.71 |

Speed and cost were measured on one 40 GB slice of an A100 with llama.cpp on 15 development cases. Quality is the mean
of two blind LLM judges over 96 runs per arm. At 8,192 tokens of context the weights and their cache take about 6.5 GB,
so the model should fit an 8 GB consumer GPU; that is an estimate, not a measurement on one.

## Quality at 4 bits

On test set 3 (12 companies never used in development, 48 cases × 2 attempts, the same harness and guards):

| Arm | Mean score (0–3) | Finished runs |
|---|---|---|
| aemon-8b, bf16 LoRA, one at a time (as evaluated) | 1.71 | 81 of 96 |
| **This file, merged, 8 at once** | **1.59** | **79 of 96** |
| Aya Expanse 8B prompted with the same harness | 1.01 | 2 of 96 |

- Against the same 8B prompted: **+0.58 [+0.51, +0.64]** (95% interval over the 12 companies), higher at all 12.
- Against the full-precision model it keeps 93% of the score: −0.12 [−0.19, −0.06], a small loss we report as
  measured (the registered "no loss" bound of −0.15 is not met).
- This arm changes three things at once: 4 bits, merged weights and 8 runs served together. On development cases,
  merging and batching alone changed nothing measurable (−0.00 [−0.09, +0.09]), so the loss most likely comes from
  quantization.

## Running it

```
llama-server -m aemon-8b-Q4_K_M.gguf -c 8192 -ngl 99 --jinja
```

The model is trained to work inside its harness: the twelve tools, the compact prompt and the decoding guards. Without
them it is just a chat model. Point the harness at the server:

```
git clone https://github.com/Two-Eyed-Ravens/aemon && cd aemon && uv sync
uv run python -m aemon.agent.run_investigations --url http://127.0.0.1:8080 --prompt compact --context 8192 \
  --recovery no_repeats,quote_menu,resample_repeats,budget,grounded_beliefs,evidence_first --cases <case ids> \
  --output runs.json
```

## How it was made

1. Aya Expanse 8B at revision `5062468b`, with the aemon-8b adapter (seed 7) merged by PEFT in bf16.
2. Converted with llama.cpp's `convert_hf_to_gguf.py` to bf16 GGUF, then `llama-quantize ... Q4_K_M`.
3. `aemon-8b-Q4_K_M.gguf` sha256 `5ad8d535d8c94756d8138a9a877cf05987a28cbe82e72322475bfbb12c9b345f`: the same bytes
   that were benchmarked and judged (rebuilt and checked before upload).

## Licence

CC BY-NC 4.0, inherited from Aya Expanse 8B; use also follows Cohere's acceptable-use policy.
