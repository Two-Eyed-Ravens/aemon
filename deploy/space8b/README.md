---
title: aemon-8b
emoji: 👁️
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
suggested_hardware: l4x1
pinned: true
license: cc-by-nc-4.0
short_description: An 8B model that investigates a strategy question
---

# aemon-8b

*weigh what is known. test what is not.*

A strategy-investigation agent: Aya Expanse 8B with adapter A ([model](https://huggingface.co/twoeyedravens/aemon-8b)),
working through a fixed investigation process over a dossier of public sources: frame the decision, state rival
theories, weigh quoted evidence for and against each, design a test, take a position and revise on new evidence.
Every quote is checked word for word against its source.

- **Sign-in.** Pick any username: a new one opens a new account, and the same one brings you back to it. There is no
  password, so a username is not private.
- **Speed.** This Space runs on one GPU and sleeps when idle; the first visit after a pause takes a few minutes to wake.
  An investigation stops after 45 steps, the budget of the evaluated runs.
- **What runs.** The configuration sent to Stage 2's test set 3: adapter A on every stage, the compact prompt and the
  six decoding guards. On development cases it beat the same model prompted with an identical scaffold by +0.72 to
  +0.88 on a 0 to 3 blind rubric across three training seeds. Served here at 8 bits with llama.cpp b12032; the
  evaluated runs used a bf16 conversion of the same weights.

Built for the Lexsi AI Hackathon, Track 3 (Agentic Fine-Tuning), by Team Two-eyed Ravens.
Code: [github.com/Two-Eyed-Ravens/aemon](https://github.com/Two-Eyed-Ravens/aemon).
