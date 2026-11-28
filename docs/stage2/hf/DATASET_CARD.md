---
license: cc-by-nc-4.0
language:
- en
pretty_name: aemon-8b Stage 2 runs, judgments and data
tags:
- agentic
- tool-use
- distillation
- evaluation
- llm-as-judge
- agenttune
- auditkit
size_categories:
- 1K<n<10K
configs:
- config_name: test3_key
  data_files: test3/test3_key.jsonl
  default: true
- config_name: test3_packets
  data_files: test3/packets.jsonl
- config_name: test3_judgments_codex
  data_files: test3/judging/codexsol170_predictions.jsonl
- config_name: test3_judgments_claude
  data_files: test3/judging/claudecode_predictions.jsonl
- config_name: development_key
  data_files: judging/keys/stage2ab_all_key.jsonl
---

# aemon-8b: Stage 2 runs, judgments and data

Team Two-eyed Ravens, Lexsi AI Hackathon, Track 3, Stage 2. Model:
[two-eyed-ravens/aemon-8b](https://huggingface.co/two-eyed-ravens/aemon-8b). Stage 1 data (dossier, cases, version 1
training rows, Stage 1 evaluations): [datasets/two-eyed-ravens/aemon](https://huggingface.co/datasets/two-eyed-ravens/aemon). Code: [github.com/Two-Eyed-Ravens/aemon](https://github.com/Two-Eyed-Ravens/aemon).

Everything behind the Stage 2 paper's numbers, development and test set 3, so each can be recomputed without running
a model.

| Folder | Contents |
|---|---|
| `screens/` | Every development screen report (45 runs per arm: 15 cases x 3 attempts): each fine-tuned and prompted arm, every training seed, every ablation and data condition, with AuditKIT summaries |
| `judging/` | Blind packets, the judge's predictions (codexsol170) and run logs per arm; merged predictions; paired reports in `recomputed/`; the answer keys mapping packets to arms in `keys/` |
| `judge_check/` | Two blind hand checks of the judge (pages, scores, agreement) and their keys |
| `retention/` | MMLU and ARC-Challenge, base against the adapter |
| `decider/` | The evidence-kind decision model's items and offline results |
| `recovery_round1/` | Teacher corrections of the student's own failure states and the rows built from them |
| `quantity/` | Rows from 43 accepted teacher investigations on 28 new training companies |
| `test3/` | Test set 3 (twelve new companies, run once): the three arms' reports, blind packets, answer key, both judges' predictions (`judging/`), run logs and the analysis (`report.json`); `frozen/` holds the frozen cases, the freeze record and the verified dossiers; `haiku/` the Claude Haiku 5.5 arm (runs, AuditKIT replay, packets, key, both judges, analysis) |

To recompute a comparison: merge the keys and predictions as in `judging/` and run the code repository's
`aemon.evaluation.judging.report` or `scripts/paper/check_numbers.py`. A packet judged more than once takes the mean
of its judgments.

`MANIFEST.json` lists each file with the file it was made from and the sha256 of the original and of the published
copy. Cluster account numbers, the cluster address and home folders are replaced by placeholders; nothing else is
changed.

Dossier excerpts are quotations of public sources, as in Stage 1; teacher outputs are Command A+'s (Apache 2.0);
judge outputs are evaluation only and were never trained on. CC-BY-NC-4.0, research use.
