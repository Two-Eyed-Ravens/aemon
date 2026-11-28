# Test set 3: the fine-tuned 8B at 4 bits

The configuration behind $0.019 per investigation, run as one more test set 3 arm under a rule registered before its run
(`docs/DECISIONS.md`, 27 November): adapter A merged into Aya Expanse 8B, quantized to Q4_K_M (sha256 `5ad8d535...`,
5.06 GB) and served 8 at once; 48 cases × 2 attempts.

| Arm | Mean score (0–3, both judges) | Finished |
|---|---|---|
| A, bf16 LoRA (as evaluated) | 1.71 | 81 of 96 |
| **A at 4 bits, merged, 8 at once** | **1.59** | **79 of 96** |
| Prompted 8B | 1.01 | 2 of 96 |

At 4 bits the agent keeps 93% of A's score (−0.12 [−0.19, −0.06]) and leads the prompted 8B by +0.58 [0.51, 0.64] at all
12 companies. Released as [two-eyed-ravens/aemon-8b-GGUF](https://huggingface.co/two-eyed-ravens/aemon-8b-GGUF).

- `q4_k_m_s8.json`: the 96 runs (job 796248, code 0aea312, `jobs.txt`).
- `packets.jsonl`, `packets_new.jsonl`, `test3_A_q4_key.jsonl`: blind packets for all four arms, the 96 new ones, the key.
- `judging/`: both judges' predictions; `report.json`: `scripts/test3/analyze.py` output.
- `run_after.sh` and the logs: the unattended fetch, judge and analysis. Claude Code's first pass hit its usage limit on
  78 packets (HTTP 429, no output); they were judged again after the reset (`claudecode_after_reset.log`).
