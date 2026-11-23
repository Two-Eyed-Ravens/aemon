---
license: cc-by-nc-4.0
base_model: CohereLabs/aya-expanse-8b
library_name: peft
language:
- en
tags:
- agentic
- tool-use
- distillation
- strategy
- lora
- agenttune
- auditkit
- gguf
pipeline_tag: text-generation
---

# aemon-8b: a strategy-investigation agent distilled into Aya Expanse 8B

*weigh what is known. test what is not.*

Team Two-eyed Ravens (Hatem Saadallah, Nour Jennane), Lexsi AI Hackathon, Track 3 (Agentic Fine-Tuning), Stage 2.
Live demo: [spaces/twoeyedravens/aemon-8b](https://huggingface.co/spaces/twoeyedravens/aemon-8b). Data and every judged run: [datasets/twoeyedravens/aemon-8b](https://huggingface.co/datasets/twoeyedravens/aemon-8b).
Stage 1 (Tiny Aya Global 3.35B): [twoeyedravens/aemon](https://huggingface.co/twoeyedravens/aemon). Code and paper: [github.com/Two-Eyed-Ravens/aemon](https://github.com/Two-Eyed-Ravens/aemon).

A LoRA adapter for [Aya Expanse 8B](https://huggingface.co/CohereLabs/aya-expanse-8b) that runs a structured
strategy investigation through twelve guarded tools: frame the decision, state rival causal theories, weigh quoted
evidence for and against each, design a test that separates them, take a position and revise on new evidence. It was
trained with AgentTune and Unsloth on replay-exact tool calls from a Command A+ teacher.

## Results (development cases, one blind judge, 45 paired runs per arm)

Against the same Aya Expanse 8B prompted with an identical scaffold (prompt, decoding guards, context, server):

| Training seed | Fine-tuned minus prompted (0–3 rubric) | Finished runs |
|---|---|---|
| 7 (this adapter) | +0.72 [+0.59, +0.85] | 39 of 45 against 4 |
| 11 | +0.88 [+0.75, +1.00] | 41 of 45 |
| 13 | +0.77 [+0.69, +0.85] | 39 of 45 |

- The gain holds on the rubric stages both runs reach (+0.59 to +0.73), so it is not only finishing more.
- General ability is unchanged: 67.9% against the base's 67.3% on 800 MMLU and ARC-Challenge items.
- The decoding guards are still needed: without them quality drops by 0.43 and finished runs by 18; resampling a
  repeated call carries most of that.
- Added data (rule-built recovery rows, teacher corrections of the student's own failures) gained at one training
  seed and not over three; rebalancing the teacher's data toward rare skills made the agent loop at two of three seeds.

## Test set 3 (twelve companies never used before, run once, two judges)

48 cases x 2 attempts = 96 runs per arm, every run scored blind by two LLM judges (Codex and Claude Code); intervals
over the 12 companies.

| Arm | Mean score (0–3, mean of judges) | Finished runs |
|---|---|---|
| Claude Haiku 5.5 (closed model, same environment; added after, rule registered before its run) | 1.92 | 70 of 91 |
| **This adapter (A, seed 7)** | **1.71** | **81 of 96** |
| Stage 1 system (Tiny Aya Global 3.35B, two adapters) | 1.58 | 82 of 96 |
| Aya Expanse 8B prompted with the same scaffold | 1.01 | 2 of 96 |

- **Fine-tuned minus prompted: +0.70 [+0.61, +0.79]**, higher at all twelve companies; Codex +0.79, Claude Code
  +0.61; +0.55 [+0.44, +0.66] on the rubric stages both reach.
- Fine-tuned minus the Stage 1 system: +0.12 [+0.05, +0.20], higher at ten of twelve companies.
- The two judges agree in sign on both comparisons (Spearman 0.78 between their run scores).
- The guards matter on held-out data: without them this adapter scores 1.23 and finishes 34 of 96; with them, +0.48
  [+0.31, +0.65] higher at all twelve companies.
- Claude Haiku 5.5 (Stage 1's staged prompt, no guards) minus this adapter: +0.20 [+0.05, +0.35] as registered; 11 of
  its 91 runs ended on API refusals, and without them, post hoc, +0.42 [+0.32, +0.52]. $0.008 per investigation.

## Files

- `aemon-8b-adapter.gguf`: the adapter as served in every evaluation (llama.cpp LoRA, bf16), sha256 490d47e3...
- `peft/`: the PEFT adapter it was converted from (rank 16, alpha 32, dropout 0.05, all linear projections).

Serve with llama.cpp on a bf16 GGUF of the base at revision `5062468b`:
`llama-server -m aya-expanse-8b-bf16.gguf --lora aemon-8b-adapter.gguf`. The agent harness, prompts and guards are in
the code repository; the adapter alone does not reproduce the agent.

## Training

Aya Expanse 8B, LoRA rank 16 on all seven linear projections (41.9M trainable parameters), two epochs, 1,971 steps,
learning rate 1e-4, loss on the target tool call only, through AgentTune's distillation trainer with Unsloth.
Data: 3,891 replay-exact Command A+ rows from 158 investigations on 57 training companies plus 51 correction rows
(3,942 in all).
Held-out loss on six validation companies 0.565 to 0.387.

## Licence and limits

CC-BY-NC-4.0, following Aya Expanse: research and non-commercial use. The dossiers support evaluating
evidence-grounded reasoning and procedure, not commercial decisions about the named companies. Quality is judged by
LLM judges on a fixed rubric; two blind hand checks agreed on the direction of differences, not on the ranking of runs.
