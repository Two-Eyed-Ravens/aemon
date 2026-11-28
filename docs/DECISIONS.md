# Decisions

Paths in entries before 2026-11-05 refer to the old layout (`strategy/`, `tooling/`, `run_agent.py`). The README maps them to `src/strategy_agent/`, `jobs/`, `scripts/`, `data/` and `reports/`.

Choices that shape the experiment, with what was considered. Change one here, openly, or not at all.

## Teacher: Aya Expanse 32B, not Claude

Decided November 2, 2026.

**Options considered.** Aya Expanse 32B, a fallback Cohere model, or Claude. Hatem offered Claude as the teacher and said it was probably the better teacher. An outside reviewer also proposed it, with a provenance record in place of the block.

**Decision.** Claude is not the teacher. Aya Expanse 32B was tried first, and its runs were rejected: it follows the workflow, but its reasoning stayed weak even with a stricter prompt (`reviews/teacher_review/`). Hatem asked for another teacher if it was bad, so Command A+ is now under test. It is a Cohere model, Apache 2.0, and not on the permitted list. Lexsi confirmed on November 2 that it is allowed, as Hatem reported.

**Why not Claude.** Anthropic's commercial terms, section D.4, say the customer may not "access the Services to build a competing product or service, including to train competing AI models or resell the Services except as expressly approved by Anthropic" (https://www.anthropic.com/legal/commercial-terms, read November 2, 2026). Training a published language model on Claude's trajectories falls within that on the plain reading. Whether a small adapter truly "competes" is arguable, but that is Anthropic's to answer.

**Two separate questions.** Whether to use a model is Hatem's decision. Whether its licence or service terms allow training on its output is checked here, because that is what this project's code does.

**What the organizers said.** Hatem reported Lexsi's reply on November 2 as "they said using antrhopic is ok", and later "lexsi said we can use claude". The question he sent asked about Claude for evaluation and harness tests only, with none of its output used for training, so the reply covers that use.

**Where each candidate stands.** Claude: eligible for evaluation, and excluded from training by its provider terms, a question Hatem has closed. Aya Expanse 32B: eligible as a listed model, licence CC-BY-NC, rejected on quality. Command A+: licence Apache 2.0, so its provider terms allow it, and Hatem confirmed on November 2 that it may be used. It is the chosen teacher, subject to the behavioural review and the protocol gates.

**What the weights hash does.** It identifies which checkpoint produced a run, so a label cannot launder an episode. It does not grant permission: permission is recorded here, and `TEACHER_WEIGHTS` only enforces it. An API teacher would need its model version, prompts, request ids and outputs recorded instead.

**Reported approval.** On November 2 Hatem reported an email from Anthropic saying this use is fine, because the model is neither commercial nor competing. He then pasted this text:

> In this scenario, you may use Claude to generate teacher demonstrations for fine-tuning Tiny Aya Global for your Lexsi hackathon project, subject to the applicable service terms. Please document the origin of the generated demonstrations and evaluate the resulting model independently.

**Status: dropped by Hatem on November 2, so the policy is unchanged.** The paste has no sender, date or signed name, so its origin cannot be confirmed from it. It is subject to the service terms, which include D.4, it does not mention D.4 or competing models, and it does not cover publishing the adapter or dataset.

**What Claude does instead.** It tests that the workflow can be completed, and it can judge transcripts. Its output cannot reach a training row, and its scores cannot decide which rows are kept. `strategy.claude_control.training_source` enforces this from an append-only manifest, identifying a teacher by the hash of its weights rather than a label.

**What would change this.** Written approval from Anthropic. The judging plan would then need revisiting, because judges must be distinct from the teacher.

## No human reviewers

Decided by Hatem on November 2, 2026, on cost. Quality comes from executable checks, paired behavioural tests and blind LLM judges. Results are described as improved performance under automated evaluation, not as proven judgment.

## Moldex-Metric is for development only

Approved by Hatem on November 2, 2026, as the development and demonstration case. The prompt, checks and reference were tuned on it, so it can never be the final test.

## The papers inspire the agent, and do not specify it

The aim of selecting among causal theories through experiments comes from Camuffo, Gambardella and Pignataro. The stages, minimums and guards are this project's own design, so public writing says "inspired by", never "implements". The differences are listed in `reviews/guard_changes/README.md`.

## Structure: the harness fixes order, the model decides content

Adopted November 2, 2026. The harness sets the stage order and minimum work. The model chooses what to search, which theories to hold, what to test and what the evidence means. Constraints may reject what does not exist. They must not choose evidence, repair an argument or write a missing theory, because that would supply what is being measured. Every refusal is logged, and the harness repairs nothing.

## No Bayesian network or belief ledger in this pilot

Decided November 2, 2026. Hatem asked for Bayesian updating if applicable. A full network would need an invented structure and probabilities. A harness-calculated ledger was proposed, and Codex argued against it, because assumed ratios could create the apparent revision we want to measure. Instead the model rates each theory on a five-point scale (very unlikely, unlikely, uncertain, likely, very likely) before and after new evidence. That is a within-run signal, not a calibrated probability. A ledger could be studied later as a separate treatment.

## Two theories, and a test only when warranted

Agreed on November 2, 2026, before freezing. Two distinct theories are the minimum and a third is optional, because the source paper compares a theory with an alternative. A model may decline a test with a reason, because committing without research can be right. Each case declares in advance whether more information is worth its cost. These are study design choices, not rules from the paper.

## Proposed: a Socratic coach

Hatem asked on November 2, 2026, for an agent like Socrates that coaches by asking questions. **Not designed yet.** It only asks and never answers. It could act inside an investigation, for example when the model loops, and in the Strategy Lab to coach the person. Inside an investigation it is part of the treatment, so it must run identically in every arm, must not supply theories, evidence choices or interpretations, and must be frozen before the final test. Its questions count as harness actions.

## 2026-11-03: the final test is frozen before more teacher data

The final test is four held-out companies, eight cases: Electrolux Professional, Aquaporin, Simonelli and RATIONAL.
RATIONAL was added to training the same day, then moved to the final test before any teacher run touched it,
because it is the same industry and mechanism as Electrolux Professional and Simonelli (professional food-service
equipment offered to home cooks). Keeping it in training would have let the final test reward a near copy.
Its case is also one where no test is warranted, which the final test lacked.

`strategy/freeze.py` digests the held-out cases and all 76 of their evidence records into
`docs/final_test_freeze.json`. The tests fail if that digest changes, if a development case can see held-out
evidence, or if a company is on both sides. No held-out case id appears in any teacher report, episode log or
row file on the cluster (checked 2026-11-03). Hellberg is development, not unseen: its loss chose the checkpoint.
Changing the final test needs a new freeze, recorded here with the reason.

## 2026-11-03: first paired pilot, and two repairs before the second

Development pilot, not a test: 10 cases from two companies (5 Moldex, 5 Hellberg), the same bf16 GGUF, controller,
prompt, tools, budgets and settings in both arms; only `--lora` differs. Base: 1 of 10 finished, mostly stopped by
repeating accepted calls early in the investigation. First adapter: 0 of 10 finished. 8 runs never left the reading
stage: the model kept searching after the budget refusal. 2 Hellberg runs reached position or revision and then hit
the context limit. Reports are in `tooling/real_model/strategy/pilot1/`. Hellberg chose the checkpoint, so it is
not unseen.

Repairs, applied identically to every arm from now on:
1. **The search count.** Each search result said `searches_left` including the search held back for
   `challenge_theory`, so at "1 left" the next search was refused. The teacher hit this 30 times and the student
   learned the habit without the recovery. The guidance now reports `searches_left` without the held-back search, plus
   `kept_for_challenge`. Guidance is added when shown and is not part of the recorded result, so recordings still replay.
2. **Stage coverage.** Rows over 8,192 tokens are refused, and full history kept only 17 of 53 conclude rows (32%), with
   update at 56% and position at 71%. The compact state now carries theories, assessments with quotes and limits, tests
   and revisions in full. Built compact, every row is kept (conclude median 4,674 tokens, maximum 5,640), and no target
   names an id missing from its context, measured by `tooling/row_coverage.py` in `row_coverage_first.json`.
   The second pilot trains on compact rows and runs every arm compact.

## Proposed 2026-11-03: specialist adapters, tested one at a time against the shared adapter

Idea (Hatem, with outside review): one Tiny Aya base with separate LoRA adapters for problem framing, theory work and
experiments, chosen by the controller per stage. Not assumed to help: each step is a comparison against the shared
adapter on the same source investigations, company split, harness, prompt and inference budget, with training compute
reported separately.

Checked before planning:
- llama.cpp b12032 holds several adapters and switches per request with no carry-over (two adapters loaded, base output
  restored exactly after a switch). `strategy.run --lora-route default=0,test=1` routes by stage, and
  `tooling/train_pilot.py --stages test` trains and validates a specialist on one stage's rows.
- Data is thin per specialist. From the 45 accepted episodes, compact: problem 90 rows (45 framings), theory 881, test
  stage 121 rows but only 45 are test designs, conclude 53. No episode declines a test, so a specialist trained now
  would learn that a test is always warranted. The first declines come from the no-test companies now in the queue.
- The "12 of 12 framed" figure is an old mechanical check on the untrained model, not a framing quality score.
- The compact state hands every stage the theories, predictions, quoted assessments, tests and revisions in full, so a
  specialist does not work from a short summary. It does not recover dropped rows by itself; compact building did that.

Order:
1. The shared compact adapter (second pilot) is the comparison.
2. An experiment specialist, trained on test-stage rows only, after the new teacher batches add declined tests.
3. Shared against shared-plus-experiment, two ways: full investigations, and test-stage prefixes, where each arm
   continues a held-out-company teacher episode replayed to the test stage. The prefixes separate test-design quality
   from earlier failures, which today stop most runs before the test stage.
4. Problem and theory specialists only if step 3 justifies them.

Responsibility: revision after a simulated result goes back to the theory adapter, and the conclusion stays with the
shared adapter unless a comparison shows otherwise.

## 2026-11-03: second paired pilot, compact in both arms

Same 10 Moldex and Hellberg cases and bf16 runtime as the first pilot; both arms run compact, and the adapter learned
from the same 45 teacher investigations built compact, so no rows were dropped (held-out loss 0.92 to 0.689, best at the
last step). Base: 0 of 10 finished, every run stopped in the evidence stage after about 7 calls. Second adapter: 1 of 10
finished, 6 reached theory building or later, mean 31 calls. Reports are in `tooling/real_model/strategy/pilot2/`.

The dominant failure in both arms is new: repeating an identical search after it was refused (41 of the base's 41
refusals, 67 of the adapter's 113). In compact mode the context after a refusal is almost the one before it, so at
temperature 0 the model writes the same call again, although the state lists what it already tried. The adapter still
searches into the held-back challenge search (33 refusals) despite the corrected count.

Test-stage prefixes, on the laptop's Q4 model, 6 Hellberg teacher prefixes: base proposed a test and left the stage in
5 of 6, the second adapter in 2 of 6; it went back to reading sources. Test-stage teacher rows are mostly reading and
assessing (76 of 121), which is a likely cause. Small, one company, Q4: a warning, not a conclusion.

No trained model is yet shown to investigate better. The second adapter is the strongest trained one and is the live
model in the Strategy Lab, labelled as a development model.

## 2026-11-03: 200 investigations, validated on six companies never trained on

Hatem's goal: about 200 accepted teacher investigations to train from, and evidence that the agent generalises.
Splits are by company, in `strategy/splits.py`. Validation is six companies never trained on: Hellberg, Neumann, Jotun,
Tanita, Deere and ACR, across six industries and including a case where no test is warranted. They set the held-out
loss, choose the checkpoint, and are the cases for every development eval and prefix test from now on. The two pilots
so far scored Moldex, which the model trained on, so they measure fitting, not generalisation. The final test stays the
four frozen companies, opened once. A gap between training-company and validation-company results is read as
memorisation. The same six are the companies in the Strategy Lab demo, so what is tried there is unseen.

## 2026-11-03: how results are worded, after outside review

- Training data is "provenance-verified, replay-valid teacher demonstrations". Replay proves authenticity and tool
  consistency, not that the teacher's theories, tests or recommendations are good.
- "No validation-loss increase observed over two epochs" on the validation rows, not "no overfitting". Validation loss is
  reported per company and as an unweighted company mean, which now chooses the checkpoint.
- Rows are counted as candidates, length refusals and rows used, for training and validation separately. The first run's
  101 refusals were 73 training rows (30 of them conclusion rows) and 28 validation rows; it trained on 902 of 975
  candidates and validated on 142 of 170. The second used all 975 and 170.
- Prefix results describe performance from a supplied teacher history. They locate weaknesses and cannot show that the
  student reaches that stage, or forms those theories, on its own.
- A converted adapter is checked numerically against its PEFT original in every eval job before results are read.
- "Got further" is replaced by `strategy/progress.py`: highest stage completed, refused and repeated calls, sources read
  and used. The pilots are inconclusive: 1 of 10 against 0 of 10, reversed between pilots.
- The defensible claim today: the pipeline learns teacher responses, and compact state prevents length-based exclusions.
  Improved autonomous strategic investigation is unproven.
- The next experiment is the recovery-data pilot in `docs/RECOVERY_PILOT.md`, compared with the second adapter before
  the full batch, once Hatem and Codex approve it.

## 2026-11-04: two teachers on 40 GB slices, one with a smaller thinking budget

gnode04 cannot run our programs (compute nodes allow-list binaries; a downloaded build gets "Operation not permitted"),
and gnode02's 80 GB slice is held by other users' CPU use until about 15:05 on 5 November. Command A+ therefore runs on
two 4g.40gb slices on gnode03, sharing the queues. Measured on a 40 GB slice with 4 slots: 19 tokens per second reading,
1.4 per second writing per slot. To speed collection up, the second teacher uses a 512-token reasoning budget instead
of 1024. Which batches used which budget is fixed by their file prefix: `cap9_*` (job 737962) used 1024, `cap8_*` (job
737966) used 512; every earlier prefix (`cap1` to `cap5`) used 1024. Acceptance, guards and progress are compared by
prefix before the final build; if the 512 batches are clearly worse, they are reported and can be excluded. The data
cutoff is no longer fixed: collection continues until about 200 accepted investigations or until the schedule needs
training to start.
Update, 21:25: on investigations the 1024-budget teacher finished none of four in 90 minutes (single turns of about
1,150 tokens at 1.5 per second, about 13 minutes each), while the 512-budget teacher finished three of four in 103
minutes, each with two rival theories, a discriminating test with a threshold, and a reasoned revision where a what-if
applied. Both teachers now run at 512 (`cap8_*` and `cap6_*`). Every manifest entry since then records its budget.

## 2026-11-05: teacher prompt v2, after a substantive review of seven accepted investigations

Seven replay-valid teacher investigations (Masimo, Statitrol, Gore, Nalgene, Tupper, SIGVARIS, Technogym) shared three
judgement flaws: evidence of a product, price, certification or marketing line scored as support for a customer
motivation; tests that contrast messages and measure stated intent; and occasionally a weak rival theory. Replay proves
authenticity and tool consistency, not quality. Masimo's base investigation is excluded from training
(`data/review/excluded_episodes.json`, with the reason); its original stays recorded.

The teacher prompt is revised to `teacher-v2` (`src/strategy_agent/common/constants/prompts.py`): numbers presented as
observed must come from a source while proposed design numbers are allowed when labelled; predictions must differ
between rivals under the same conditions (no blanket metric ban); each rival needs a credible mechanism and bearing
evidence; evidence direction is judged against a specific claim, distinguishing capability, motivation, purchasing
behaviour and value capture; tests explain why they distinguish mechanisms, name alternative explanations and prefer
consequential behaviour without requiring it. The shared number rule changes in the student prompt too. Every new
manifest entry records `prompt_version`; earlier demonstrations keep their original version and protocol id.

The third-adapter comparison keeps its frozen dataset (episodes collected before v2, minus the Masimo exclusion) so it
still measures the effect of more data. A screener from the judge package will flag substantive weaknesses with recorded
reasons; a high score is not proof of correctness, and valid investigations need not reach the same recommendation.
Known limitation: historical cases include sources written after the decision date (flagged in each record); they can
reveal outcomes, so hindsight is not evidence that a recommendation was right, and the screener is asked to flag its use.

## 2026-11-05: conversion gate measured against the no-adapter baseline

The second adapter's conversion check (eval job 738581) failed only on the absolute rule "top-10 log-probability gap at
most 0.15": worst gap 0.245, with the first token agreeing on 8 of 8 prompts and 25.2 of 32 greedy tokens. The check also
measures each prompt with the adapter off, and the base model alone, with no adapter, differed by up to 0.19 between
Transformers and llama.cpp at 4K-token contexts. An absolute 0.15 therefore failed the base conversion itself and
measured kernel differences, not the adapter conversion. The adapter's own effect was 7.9 to 19.3 on the same scale.

New rule, before any evaluation result exists: on each prompt the converted adapter may add at most 0.15 to that
prompt's gap without the adapter (worst observed: 0.074), and no gap may exceed 0.5. The first-token, greedy-agreement
and adapter-effect rules are unchanged. This loosens a gate after it failed, so it is recorded here, the failing JSON is
kept at `runs/eval/val_second_conversion.json` on the cluster, and is reviewed before the freeze.

The third adapter's job (738584) crashed with a division by zero because its correction share was set to 0 for the
data-quantity comparison; a share of 0 now means teacher rows only.

## 2026-11-05: data-quantity diagnostic, and targeted corrections

The third adapter (82 accepted investigations, frozen report list `rows/third_reports.txt`, no corrections) failed the
conversion gate narrowly (mean greedy agreement 23.4 of 32 against 24; one prompt added 0.158 against 0.15; first token
8 of 8). Its validation run was made as a labelled diagnostic (`DIAGNOSTIC=1`), which selects nothing. On the 15
validation cases, one attempt each, mechanical measures only: the second adapter finished 2, stopping otherwise in
theories (10), assessment (1) and conclude (2); the third finished none, stopping in theories (8) or looping in the
test stage after completing the challenge (7, all 117 of its test-stage repeats). This does not show that more data
improved completion, and with conversion unresolved it cannot show that the larger dataset made the agent worse.
Recovery from loops is a plausible remedy, not a proven one.

The conversion is to be diagnosed (a real error against greedy changes at near-ties) with tolerances
that apply to every adapter, the second included, with the 2026-11-05 baseline-relative rule under review. Test-stage
correction states come only from the third adapter's runs on 24 training-company base cases; no validation trajectory
becomes a demonstration. The schedule is unchanged: v2 collection continues, then conversion, targeted corrections and
the final training by Saturday 7 November, 18:00 CET.

Test-stage corrections: each state carries the student's adapter and runtime identity, including the failed conversion
check, because the loop may come from training, conversion or their interaction. A correction from a test-stage state
counts only if it proposes a test with different predictions for at least two theories, a numeric decision rule and a
why_next that names the theories it separates, or declines a test with a reason; a valid, non-repeated call alone is
refused. No further batch is collected to reach a count: the final run uses the valid corrections available and reports
their actual share of supervised tokens. Once Codex resolves conversion, the same check is applied to the second and
third adapters; if a real conversion bug is found, the repaired third adapter is re-run on the existing development
cases before its earlier behaviour is interpreted. The latest training start stays Saturday 7 November, 18:00 CET.

## 2026-11-05: the compact state lists reads, and says an excerpt is everything the dossier holds

The 16 test-stage correction states were answered by Command A+ (batch correct5): 14 replies re-read a source, 9 of them
exact repeats. Only 1 of 16 passes the test-stage rule (kes: a discriminating test). In the festool state the teacher
reasoned that a 93-character excerpt "only shows a snippet; its full content may reveal" more, and read it again. 602 of
1,334 dossier excerpts are under 150 characters; rereading is free and unmarked in `read_source`; and the compact
state's `already_tried`, the list the prompt says not to repeat, held searches and challenges but never reads. Teacher
rows teach the loop little: 51 of 2,083 training rows are rereads, 2 of them in the test stage. The teacher's stated
reason and the short-excerpt counts make the interface a plausible contributor to the loop. They do not measure how
much it contributes, and they do not show that training or corrections cannot help.

Change, Hatem's choice of three options: only the compact state changes. `already_tried` now includes `read_source`
calls (the last 12 entries instead of 8), and a `sources_note` says each excerpt in `sources_read` is everything the
dossier holds for that source. Tool results are unchanged, so all 114 collected teacher episodes still replay
(checked), and the running teachers, whose prompt shows full history rather than the compact state, are unaffected.
Training rows and every later evaluation, both arms, use the new state; correction rows rebuild their context by replay
in the same format. The longest compact row was 5,890 tokens against the 8,192 limit, so the few added entries fit; the
training job's row-coverage gate checks this again. Earlier development results were made under the old state and are
not compared directly with later ones. This is reviewed as a protocol change before the freeze.

Wording: an excerpt is everything the dossier holds for a source, not the whole original source; `SOURCES_NOTE` says
exactly that, and the commit title of ebdeca7 ("the whole source") is imprecise. The change removes an observed
ambiguity; it is not shown to reduce loops, and the next matched evaluation measures that. Short excerpts still limit
what an investigation can establish: making their completeness clear stops futile retrieval but supplies no missing
context and justifies no stronger conclusion. Results made before ebdeca7 (the second-adapter and third-adapter
development runs, protocol d8c0295994fd, and the 24 training-company student runs) are kept as a separate protocol
version; the runner's protocol id changes with the state, so later runs are told apart automatically. The final rows,
the correction contexts and both arms of every later evaluation use the new state. Surviving corrections are used even
if their share of supervised tokens falls well below 20%, and the training report gives the actual share.

Corrections asked before ebdeca7 (review of ebdeca7, option a): the teacher answered the old state, so its
reply is not turned into a row under the new one. `corrections rows` now keeps a correction only if the context the
teacher was sent equals the context replay gives today, and skips any other. The 23 corrections that survive the
current judge (12 from cap8_correct0, 10 from cap9_correct1, 1 from correct5) are asked again on the new state as batch
correct6, first in the queue; the queued batches correct2 to correct4 were rebuilt in the new format before any
teacher took them (originals in `queue/states/old/`). Old replies and their manifest entries stay as they were. New
corrections should also bind the exact outgoing request when #25's source bindings are ported; the old ones lack it.

## 2026-11-06: training data accounting before the freeze, and when the final run starts

Built at 12:40 with the training job's own steps (code 20d3610, compact state of ebdeca7) from the 49 teacher reports
and 7 correction files on the cluster, while collection continues:

- 158 replay-accepted investigations: 142 from training companies and 16 from validation companies (hellberg 6, and 2
  each from tanita, neumann, deere, acr and jotun). 27 did not replay to an accepted finish and Masimo is excluded on review.
- 3,895 teacher rows: 3,484 from 58 training companies and 411 from the 6 validation companies, which are used only for
  the company-balanced validation loss. None comes from the 4 frozen final-test companies (aqp, epro, rational, simo).
- Corrections: 80 provisionally kept replies, of which 51 become rows; none is from a validation company. The rest
  failed re-judging (6, all test-stage) or were asked under the old state and re-asked as correct6 (23). No test-stage
  correction survives: 49 rows are in theories, 1 in assessment, 1 in conclude.
- Supervised tokens, training companies only (validation rows excluded): 354,220 from the 3,484 teacher rows and 1,251
  from the 51 corrections, so 0.35% of training tokens (1.44% of training rows). Each correction
  is used once; none is duplicated to approach the 20% budget.
- Gates: row coverage (compact) refuses 0 rows for length and finds 0 targets naming something missing from their
  context; the longest row is 6,011 of 8,192 tokens. Every row passes the loss-mask prefix check. The split test
  passes. The model-level masking gate (`training/masking_gate.py`) passed in the pilots and is not re-run; the
  training job's overfit gate runs before the full run.

Collection closes when the queued batches are done (about 03:00 on Saturday): replacement teachers take over when the
running ones reach their 22 hours. The final training (NAME=final, code 20d3610, compact rows, 2 epochs, checkpoints
every 50 steps, corrections capped at 20%) then starts by Slurm dependency, with no further pilot or collection target,
and the job's decisions and coverage files record the frozen report list and final counts. Conversion stays separate:
it must be resolved before converted-model evaluations are interpreted or that format is released, not before
training. If it is still unresolved at evaluation time, the PEFT adapter is evaluated against the base in the same
Transformers runtime, if that fits the schedule, and the converted demo stays labelled as unverified.

Submission: the final training is submitted by Slurm, not by a chat session. The replacement teacher 741931
(`~/lexsi/teacher_then_train.sbatch`, behind 740314) submits it when it finds the queue empty, with a dependency on the
other replacement 741924 if that still runs. A check from the login node submits it earlier if a job slot opens, with
dependencies on both. The marker `rows/final.submitted` records the job id and stops a second submission. Submitting
from inside a compute-node job is not yet tested on this cluster.

Submitted: job 742209, from the login node at 15:48:49 on 2026-11-06, with `--dependency=afterany:741924:741931`, so it
starts when both replacement teachers have emptied the queue. Before that, the gnode01 teacher (739879) hit its Slurm
time limit at 15:38 partway through batch again1, which went back to the front of the queue; its partial episodes
wrote no report, so nothing is counted twice.

What the run tests: mainly more teacher demonstrations (142 training-company investigations against the third adapter's
72; its 82 accepted included 10 from validation companies) together with the clearer compact state. Corrections are 0.35% of training tokens and none is from the test stage,
so it is not a substantial test of recovery training, and its results are not presented as one.

## 2026-11-06: two blind judges, Claude through the API and Codex

PR #24 (judge-v1: nine-dimension rubric, prompt, six anchors, 40-packet blinded qualification set, 14 offline probes
passing, hashes matching `config_v1.json`) is merged. Hatem chose the two judges: Claude through the existing API key,
which is approved for judging only and capped by the spending ledger, and Codex (OpenAI, through the Codex CLI on
Hatem's ChatGPT account). Neither is the student or the teacher, as FINAL_EVAL_PLAN requires. An earlier version of
this entry (289cee4) said one judge; it was written before Hatem's answer was complete and is superseded.

Codex wrote the rubric, the anchors and the qualification set with its answer keys. So the Codex judge is a fresh,
isolated run that receives only the judge prompt and one packet: no repository, no keys, no session memory. The same
applies to Claude. Each judge must pass the qualification set under `config_v1.json`'s rule before it scores any
evaluation episode, with its exact model id and settings recorded. Arm names are removed and packet order is
randomised. Each judge is reported separately, with their agreement. Judge output never selects or filters training
data.

The question the evaluation answers: under the same new compact state, does the trained agent produce better
investigations than the base, judged on credible, distinct causal theories (causal_mechanism, distinct_theories),
evidence that supports the specific claim made (evidence_judgement), tests that distinguish those theories
(experiment_design), and justified revisions and recommendations (revision, recommendation), alongside the mechanical
progress measures. The claim follows the results.

## 2026-11-06: how a judge qualifies for evaluation scoring (written before it is computed)

The Claude judge (claude-opus-5-5) ran the 40-packet qualification under config_v1 and is `not_qualified` there: 20 of
20 flawed packets rejected, 9 of the 12 sound packets with valid output accepted, and 8 outputs invalid (7 calling a
trajectory suitable for training while listing a critical red flag, 1 API error). That rule qualifies a training-data
screener on a binary suitability decision. Evaluation uses only the 0 to 3 dimension scores, so Hatem chose a separate
rule for scoring, recorded here before anyone computes it for any judge:

- For scoring, an output is valid if its response parses as JSON and its dimension block passes judge.validate's
  dimension checks: every dimension present, status scored, not_reached or not_applicable as the packet's applicability
  requires, integer scores 0 to 3 only when scored, event ids that exist in the packet, a reason for each. The screening
  fields (suitable_for_training, red_flags, screen_reason) are ignored for scoring.
- An invalid output is retried once, the retry recorded beside the original. After the retry, at most 4 of the 40
  outputs (10%) may be invalid.
- A packet's score is the mean over its applicable dimensions, with not_reached counted as 0.
- Each of the 20 clusters pairs a sound and a flawed version of one case. The judge qualifies for scoring if the sound
  version scores strictly higher in at least 17 of the 20 clusters. A tie, or a cluster with an invalid output, counts
  as a failure.
- The frozen config_v1 screener rule is unchanged and still governs any use of a judge as a screener. No judge
  screens training data.

## 2026-11-06: six investigations at once on the second replacement teacher

To try to speed up collection, Hatem chose to run the second replacement teacher with 6 parallel slots instead of 4 (a
smaller teacher quantisation was ruled out). With most of Command A+ in node memory, a step's cost is dominated by
reading the weights, so more slots may raise total throughput; more KV cache could instead push layers to the CPU, so
it is measured, not assumed. Because a batch's investigations run in parallel and most batches hold 4 cases, that
teacher (job 742354, replacing 741931 and 742352 before they started) takes merged batches first from its own queue
`teacher_six.txt`: six0 (again4 and again6), six1 (again5 and again10), six2 (again7 and again11) and six3 (energyagain0
and energyagain1, 8 cases). Then it falls back to the shared queue, which keeps 6 four-case batches for the 4-slot
teacher 741924. The original queue is kept at `queue/old/teacher_later.before-six.txt`. Teacher settings, cases and
seeds are unchanged; the server records its slot count in every manifest entry. The final training (742209) now
waits on 741924 and 742354. If 6 slots turn out slower, the remaining six-case batches go back to the shared queue and
the next teacher uses 4.

Qualification results (2026-11-06). Claude (claude-opus-5-5): qualified for scoring, with 19 of 20 clusters ordered and
1 of 40 invalid after one retry (a response cut at max_tokens). Not qualified as a screener: 20/20 flawed rejected,
9/12 sound accepted, 8 invalid screening outputs. Codex (gpt-6-astra, codex-cli 0.166.0, an isolated ephemeral
read-only run per packet): qualified both as a screener (20/20 sound accepted, 20/20 flawed rejected, no errors) and
for scoring (20 of 20 ordered, 0 invalid). Its run was interrupted twice by the ChatGPT usage limit and once by a
failed cloud-config fetch; those infrastructure failures were archived (`results/codex_archived_*`) and only they were
judged again, never a valid judgment. Caveat for the report: Codex wrote the qualification packets and keys. Each judge
call saw only the prompt and the packet, but a judge may still score its own author's examples more consistently, so
the qualification is weaker evidence for Codex than for Claude. Neither judge screens training data.

Six slots, outcome (2026-11-06, 22:30): withdrawn. The six-slot teacher (742354) finished six0 (6 investigations, 5
finished) and was then killed for running out of memory during six1: the 135 GB model held in node memory plus six
slots of context exceeded the job's 200 GB limit. six1 produced no episodes and its report holds no records, so
nothing from it enters the rows. six1 and the unstarted six2 and six3 went back to the shared queue as their original
4- and 2-case batches, and a 4-slot replacement teacher (742871) was submitted. The final training (742209) now waits
on 741924 and 742871. Correction: the 7.4 and 7.7 tokens per second per slot I reported for the six- and four-slot
teachers came from the prompt-reading lines of the server log, not generation. Generation is about 1.2 to 1.3 tokens
per second per slot in both, so the "about 40% more output" figure was unsupported, and no speed-up was shown.

## 2026-11-06: conversion gate v2, from the diagnosis (registered before the final adapter exists)

Codex's read-only diagnosis (job 742630, code 12fdae7, greedy set explicitly in both backends) on the second and
third adapters, 8 prompts each: the converted adapter reproduces the PEFT adapter's effect over the full 262,144-token
vocabulary with effect cosine 0.9975 or more (mostly above 0.9999), and the probability-weighted residual is at most
0.142. Rounding the PEFT factors to BF16 leaves that residual unchanged, so factor precision is not the cause; the
remainder is backend arithmetic. With the adapter off, the base alone diverged between Transformers and llama.cpp on 4
of the third adapter's 8 prompts. Where adapted greedy traces parted, PEFT's top-1/top-2 margin was 0.0 (second
adapter), 0.125 and 0.75 (third), against 12 to 14 elsewhere; several earlier 'disagreements' were one side stopping
at an end token. No conversion defect was found. A near-tie flip can still change a trajectory, so converted-model
results are read with that caveat.

Gate v2, for every adapter (the second and third included): on every replayed point, effect cosine at least 0.99 and
probability-weighted effect residual at most 0.15; the tensor audit status `factor_pair_matches_expected_cast`. Greedy
divergences are reported with their margins and with whether the base alone diverges on the same prompt, and do not
by themselves fail the gate. These thresholds were proposed after seeing the second and third adapters' diagnostics
(both pass) and are fixed here before the final adapter exists, and reviewed. The final adapter gets the same
diagnosis inside the training job, on its GPU, right after training. Gate v1 (fe0db0a and its predecessors) is retired.
Applied: the second adapter passes gate v2 (9 points, lowest cosine 0.9997, largest residual 0.073; one greedy
divergence at PEFT margin 0.0) and so does the third (12 points, 0.9975, 0.142; one divergence at margin 0.125, on a
prompt where the base alone also diverged). Results: `reports/conversion/{second,third}_gate_v2.json`. The final
training was resubmitted as job 742970 (replacing 742209 before it started, same dependencies on 741924 and 742871)
so that it runs gate v2 on the final adapter on its own GPU before submitting the evaluations.

## 2026-11-07: final training is job 744559

Collection closed at 14:25: teacher 742871 stopped at 04:47 after its batch again7 failed its check (1 of 4 finished,
the job stops by design), and teacher 741924 ran the rest of the queue, its last batch ingragain2 ending at 14:25.
Job 742970 then started and failed at its first command (`module: command not found`, exit 127): it had been submitted
with `env -i`, which drops the exported `module` function, and the development evaluations it submits use `env -i` too.
Fix bc7bd6c loads `/etc/profile.d/modules.sh` when `module` is missing, in every job script, and changes nothing else.
The final training was resubmitted at 14:36 as **job 744559** with the same settings (NAME=final, REVISION=20d3610,
GATE_REVISION=bc7bd6c, COMPACT=1, ROW_PROMPT=compact, EPOCHS=2, SAVE=50), no dependency, without `env -i`. It built
4,302 rows, 51 of them correction rows, from 54 teacher stage reports; the accepted-investigation, token and
coverage counts are recorded at the freeze.
Job 744559 finished training at 19:14 (1,971 steps, two passes; best held-out loss about 0.713 at the last checkpoint,
which is the adapter kept) and submitted the three development evaluations: dev_final 745203, dev_second_newstate
745204, dev_base_staged 745205. Its gate v2 step did not run: the diagnosis was called with `NAME=${NAME}_final` before
`REFERENCE_REPORT=...${NAME}...` on one line, and bash expands prefix assignments in order, so it looked for
`final_final_gate_check.json`. The conversion check itself (`final_gate_check.json`) and the converted adapter exist,
so the diagnosis runs on its own as job 745209 with the right paths, and gate v2 is applied to its output. The step
is fixed in the job script (paths computed before NAME changes) for any later run.
At 19:25 the cluster home reached its 50 GB quota (50.5 GB used), and 11 of the 15 base-arm episodes of dev_final
failed in the harness with `Disk quota exceeded`; the other four and the adapter arms ran on a full disk. Those runs are
invalid and were moved, not deleted, to `runs/eval/invalid_quota_20261107/`; 745203 and 745204 were cancelled. With
Hatem's approval the unused Aya Expanse 32B teacher model (19.8 GB, replaced by Command A+; its provenance is kept at
`runs/aya-expanse-32b-Q4_K_M.provenance.removed-2026-11-07`) was deleted, leaving 30 of 50 GB used. The final adapter
had been written at 19:14 and is complete (504 tensors, size matching its header). The evaluations were resubmitted
unchanged: dev_final 745247, dev_second_newstate 745248; dev_base_staged 745205 and the diagnosis 745209 had been held and then released. Final held-out loss 0.7125 (epoch 1.999).
Gate v2 on the final adapter (diagnosis 745209, applied on the laptop with conversion_gate.py): **passed**. 11 points,
lowest effect cosine 0.9990, largest probability-weighted residual 0.080, tensor audit as expected; one greedy
divergence (hellberg-new-evidence-irrelevant, theories stage, offset 21) where PEFT's top-two margin was 0.0 and the
base alone also diverged. Result: `reports/conversion/final_gate_v2.json`. The development evaluation of the converted
final adapter is therefore readable; its outputs still carry the DIAGNOSTIC marker from the retired v1 gate.

## 2026-11-07: development judging, and the Claude judge's output limit

The blinded development packets were built from the four development arms (base_compact, base_staged, second, final;
15 runs each): 56 distinct packets for 60 runs, four base runs being identical. The key is kept outside the repository
while the judges run. Both judges run under the evaluation-scoring qualification (`run_campaign.py` now accepts
`qualified_for_scoring`, the rule registered on 2026-11-06, as well as the stricter screener status).
The first Claude attempts failed: once on a missing `anthropic` module (system Python; no call was made), then five
packets ended with `max_tokens` (cost USD 0.29), because evaluation packets are longer than the qualification ones.
Claude's output limit is raised from 3,000 to 8,000 tokens (`backends_v1.json`, version judge-v1-two-backends-2) before
any development packet was scored. Nothing else changes; every qualification judgment finished under 3,000 tokens
(largest 2,728), so the qualification result is unaffected. The failed attempts are archived, not reused.

## 2026-11-07: development results (6 validation companies, 15 cases, one attempt each)

Both judges scored all 56 packets validly (0 invalid, 0 missing). Episode score: mean of the applicable dimensions,
0-3, not_reached counted 0. They agree closely on ordering (Spearman 0.95 over 60 episodes, mean absolute difference
0.27); Codex scores higher throughout.

| arm | finished | Claude | Codex | mean of judges |
|---|---|---|---|---|
| base, compact prompt | 0/15 | 0.12 | 0.16 | 0.14 |
| base, staged prompt | 0/15 | 0.35 | 0.52 | 0.43 |
| second adapter, compact state | 6/15 | 0.88 | 1.31 | 1.09 |
| final adapter, compact state | 7/15 | 1.09 | 1.49 | 1.29 |

Paired differences, mean of judges, 95% case-cluster bootstrap: final minus base compact +1.15 [0.87, 1.42]; final
minus base staged +0.86 [0.61, 1.11]; final minus second +0.20 [-0.09, 0.53]; base staged minus base compact +0.30
[0.18, 0.42]. Each judge alone gives the same signs and the same intervals' relation to zero. Read: on these
validation companies the final adapter scores clearly above the base model under either prompt, and is not
distinguishable from the second adapter. 15 cases from 6 companies, one attempt each; Jotun shows almost no gain
(+0.21). Claude judging cost USD 4.46 (ledger 9.75 -> 14.21). Reports: `reports/judge/dev/`.

## 2026-11-07: choices from development, and the freeze

**Choices** (FINAL_EVAL_PLAN rule: higher mean blind-judge score on the validation cases, completion breaking a tie):
- Base prompt for the final test: **staged** (mean of judges 0.43 against compact's 0.14).
- Trained arm: **the final adapter** (`runs/final_pilot/adapter`, job 744559, gate v2 passed; mean of judges 1.29
  against the second adapter's 1.09). The second adapter is not used.

**The final test campaign, frozen here before any final-test output exists:**
- Cases: all 8 in `data/dossier/cases_heldout.json` (aqp, epro, rational, simo; base and irrelevant-evidence each). PR #23
  is not merged, so its packets are not included. The held-out digest matches `docs/final_test_freeze.json`, and no
  training row (`rows/final.jsonl`, 4,302 rows, 63 companies) mentions a held-out company.
- Arms: base = Tiny Aya bf16 GGUF, staged prompt, no adapter; trained = the same GGUF with the final adapter, compact
  prompt. Same llama.cpp build, context 12,288, 520 tokens per turn, 45 turns, 4 errors in a row, temperature 0
  (0.4 only on a retry straight after a refused call).
- Three attempts per case and arm (attempts 0, 1, 2; `ATTEMPTS=3` in `jobs/eval_adapter.sbatch`), 48 runs. Runner code
  revision 20d3610, the same as development.
- Infrastructure retries only (harness or server failure, same seed, at most twice, logged); never for model behaviour.
- Judging: the judge-v1 package, backends version judge-v1-two-backends-2, both judges under the scoring
  qualification; packets by `judge_packets.py` (seed 20261106), key kept outside the repository while judging; report
  by `judge_report.py`. Primary result: trained minus base, mean of the two judges, paired by case and attempt, 95%
  case-cluster bootstrap; each judge separately, each company separately, all missing runs. Negative controls:
  `fixed_policies.py` on the same cases. Mechanical measures from the runner summary.
- Claim wording as in FINAL_EVAL_PLAN: at most "on four companies it never saw ... scored X against the prompted
  base's Y under a blind LLM rubric", with per-company results; four companies support only a limited claim.
After this entry nothing in the campaign or its analysis changes.

## 2026-11-07: correction (after review), and the freeze is not yet in force

- **My claim was wrong.** I wrote that every Claude qualification judgment finished under 3,000 tokens and that the
  qualification is therefore unaffected by raising the limit. One qualification packet (0e3184f1b3aa2234, sound q09) hit
  `max_tokens` on both its first call and its retry; it was the one invalid output in the receipt. The claim held only
  for the outputs that finished. The same wrong sentence is in the `max_tokens_change` note of `backends_v1.json`; that
  file is left unchanged because its digest binds the Claude development judgments and the requalification, and this
  entry is the correction. The old receipt (`reports/judge/claude_score_qualification.json`, under 3,000 tokens) is kept.
- **Claude is requalified** on the same frozen 40 packets under the 8,000-token configuration, with the same rule
  (one retry for invalid outputs, at most 4 of 40 invalid, sound above flawed in at least 17 of 20). Until it passes,
  the Claude development scores are provisional and the choices are not final. Receipts now record the digest of the
  configuration their results were produced under, and `run_campaign.py` refuses a judge whose receipt does not match
  its current settings.
- **The freeze recorded above is withdrawn** until these are closed: the Claude requalification; the held-out scope
  (Hatem chose to include PR #23's supporting and undermining what-if pairs, so the final test has 16 cases and 96
  runs after review, merge and refreeze); the conversion evidence that the evaluated GGUF matches the one gated; and an
  exclusion manifest for the quota-failed runs. No final-test output exists.
- Neither the 0.20 [-0.09, 0.53] final-minus-second interval nor any other development result shows the two adapters
  are equivalent; the second adapter is the specified fallback, not shown interchangeable.
- The 56 packets are the 60 development runs with four identical runs sharing one judgment; every analysis uses all 60
  key rows, and the bootstrap resamples cases, not packets.


## 2026-11-04: reviewed pre-evaluation shock amendment

PR #23 was rebased on the published final-run branch after RATIONAL moved out of training. Its base and irrelevant cases remain, and each of the four held-out companies now also has a matched supporting/undermining hypothetical packet. RATIONAL's packets concern installation coordination among eligible homes; they do not erase physical requirements or the case's no-test-warranted assumption. Its stale split=training tags are corrected to heldout. Sixteen variants remain four company/question clusters and are exploratory. No held-out actor model runs were used by Codex to write or select these packets.

The preceding freeze digest was `a228c6fc694028b458ad528e4d5e3accb6f02ac3798088fbc7776d888035297d`. The deliberately regenerated digest is `dce26d4f11232f74a2d4e4b744a7ebc0c52a9c3cc04bb71f8994ea7f499ee77e` over the same 76 held-out evidence records. Regeneration used `python -m strategy_agent.pipeline.freeze > docs/final_test_freeze.json` in an isolated copy of the current freeze module/data, preserving the shared checkout. This pre-final-run amendment requires review before final evaluation; it adds no training data and grants no teacher or publication permissions. Prior freeze records remain in Git history.

2026-11-05: ported to src/data layout on main29c91f1. Packet bytes and the recorded content freeze digest are unchanged; no actor outputs inspected.

## 2026-11-07: the freeze (supersedes the withdrawn entry above)

Closed before the freeze: Claude requalified under the 8,000-token configuration on the frozen 40 packets
(`reports/judge/claude_score_qualification_8000.json`: sound above flawed in 20 of 20 clusters, 0 invalid, no retry
needed; bound to manifest judge-v1-two-backends-2, judge config sha256 14a9fc0e...; cost USD 2.59), so the Claude
development scores stand under the configuration they were produced with. Codex's receipt is re-issued bound to the
manifest its results were produced under (`reports/judge/codex_score_qualification_bound.json`; its settings are
unchanged). PR #23 is merged (16 held-out cases, digest dce26d4f...). The evaluated GGUFs match the gated ones
(`reports/conversion/evaluated_gguf_hashes.json`, compact replay beside it). The quota-failed runs are excluded
(`reports/eval/dev_quota_exclusions.json`).

**Choices, from development only:** base prompt **staged** (0.43 against compact 0.14, mean of judges); trained arm
**the final adapter** (1.29 against the second adapter's 1.09). Not shown equivalent to the second adapter.

**Final test campaign:**
- Cases: the 16 in `data/dossier/cases_heldout.json` at digest dce26d4f11232f74a2d4e4b744a7ebc0c52a9c3cc04bb71f8994ea7f499ee77e
  (per company: base, irrelevant evidence, and a supporting and an undermining what-if result). Four companies.
- Arms: base = Tiny Aya bf16 GGUF, `staged` prompt, no adapter (job NAME final_test_base, SKIP_ADAPTER=1); trained =
  the same GGUF with the final adapter (`runs/final_pilot/adapter`, converted GGUF expected sha256 41794b57...), `compact`
  prompt (final_test_trained, SKIP_BASE=1, DIAGNOSTIC=1 because the retired v1 check still runs and is marked). Both:
  SPLIT=heldout, ATTEMPTS=3 (attempts 0-2), runner code d3aa608 (identical to development's 20d3610 except the split
  option), job script `jobs/eval_adapter.sbatch` at 0377eae, same llama.cpp build, context 12,288, 520 tokens per turn,
  45 turns, 4 errors in a row, temperature 0 with 0.4 only on a retry after a refused call. 96 runs.
- Infrastructure retries only, as in FINAL_EVAL_PLAN: a whole failed job is rerun with the same configuration, logged with
  cause and times; never because of model behaviour; nothing is filled in case by case.
- Judging: both judges under the receipts above, unchanged instrument; packets by `judge_packets.py --split heldout`
  (seed 20261106), key kept outside the repository while judging; `judge_report.py`. Primary result: trained minus base,
  mean of the two judges, paired by case and attempt, 95% case-cluster bootstrap. Also each judge separately, each
  company separately, by evidence direction (supporting, undermining, irrelevant, base), all missing runs, the
  mechanical measures, and the negative controls (`fixed_policies.py --heldout`).
- Claim wording as in FINAL_EVAL_PLAN. Three attempts per case are not independent replications, and four companies
  support only a limited claim about generalisation.
Nothing in the campaign or its analysis changes after this entry.
Final test submitted at 21:00 on 2026-11-07 after Hatem's go: trained arm job 745481 (final_test_trained), base arm
job 745482 (final_test_base), both from `~/lexsi/eval_adapter.sbatch` (0377eae) with REVISION=d3aa608, SPLIT=heldout,
ATTEMPTS=3 and the 16 held-out ids.
Deviation from the freeze, found while the judges ran: `fixed_policies.py --heldout` cannot run on the held-out
cases. Its scripted policies search with fixed hearing-protection queries ('earplugs comfort', ...) and reach the
assessment step with no source read (IndexError on the empty read set), because they were written for the original
earplug cases. The negative controls are therefore not reported for the held-out set; writing a new scripted policy
now would change the analysis after the freeze, so it is not done. The development-case negative controls stand as
recorded before. This affects no model run and no judgment.
Infrastructure failures during final judging (not judge behaviour, handled as in the qualification campaigns): Codex
hit the account's usage limit partway through ("You've hit your usage limit. Try again at 11:38 PM"), so 51 packets
failed before a model turn and one more timed out in the sandbox; 35 judgments are valid. After the reset the failed
attempts are moved to `codex_archived_usage_limit/` (kept) and only those packets are judged again under the same
instrument, packets and receipt. One Claude call ended in an APITimeoutError with no response; it gets the same
treatment after Claude's campaign ends. No valid judgment is redone or replaced.
The first Codex retry (23:41) still met the usage limit: the CLI's "11:38 PM" is an hour behind local time, as with
the earlier 17:33 reset. It was stopped after 16 more failures; those and the two attempts interrupted by stopping it
are archived in `codex_archived_usage_limit_2/`. A retry from 00:45 stops itself on two usage-limit failures, archives
them, and tries again every 30 minutes, at most four rounds. Claude's two connection failures (one timeout, one
connection error) were re-judged validly under the same instrument; its third invalid output (JSON with trailing text)
is the judge's own response and stays missing, since no retry for judge output was declared.

## 2026-11-08: final test result (four held-out companies, frozen campaign)

All 96 runs completed with no infrastructure failure. Codex judged all 87 packets validly after the usage-limit
retries (round 3, 00:43-00:55, 52 of 52 valid); Claude judged 86 of 87 (one judge-invalid output, so one base run,
simo-new-evidence-irrelevant, has no Claude score and is reported missing). The judges agree closely on ordering
(Spearman 0.94 over 95 episodes, mean absolute difference 0.38); Codex scores higher throughout.

Mechanical: base finished 4 of 48 (1 passing every check); trained finished 28 of 48 (1 passing every check).

| | base (staged prompt) | trained (final adapter) | trained minus base, paired, 95% case-cluster bootstrap |
|---|---|---|---|
| Claude | 0.56 | 1.20 | +0.64 [0.51, 0.77] |
| Codex | 0.74 | 1.77 | +1.03 [0.87, 1.18] |
| **mean of judges (primary)** | **0.65** | **1.48** | **+0.83 [0.69, 0.97]**, 47 pairs, 16 cases |

By company (mean of judges): aqp +1.10, epro +0.60, rational +0.66, simo +0.98; every company positive under both
judges. By evidence (mean of judges): base case +0.84 [0.71, 0.98]; irrelevant +0.87 [0.39, 1.33]; supporting
+0.86 [0.68, 1.02]; undermining +0.76 [0.58, 1.01]. Largest dimension gains (Codex): distinct theories 0.98 -> 2.56,
framing 1.00 -> 2.90, causal mechanism 1.15 -> 2.63, revision 0.03 -> 0.81; weakest for the trained arm: recommendation
0.58, revision 0.81, experiment design 1.08, evidence judgement 1.17.

Claim, in the frozen wording: on four companies it never saw, under the same investigation setup, the fine-tuned agent
scored 1.48 against the prompted base's 0.65 on a 0-3 blind LLM rubric (mean of two judges; +0.83, 95% interval 0.69
to 0.97), higher at every company. Four companies support only a limited claim about generalisation; three attempts per
case are not independent replications; 20 of 48 trained runs still stop before a recommendation, and the negative
controls could not be run on these cases (deviation above). Nothing about business outcomes. Reports:
`reports/judge/final/`.

## 2026-11-08: diagnosis of the mechanical failures (post hoc)

`docs/FINAL_TEST_DIAGNOSIS.md`: why 20 of 48 trained runs stop and 27 of the 28 finished ones miss at least one check.
Main causes: no training row ever declines a test (the teacher proposed one in all 15 training cases that warrant
none, and half the final cases warrant none); only 8 of 205 teacher investigations on training companies had
supporting or undermining what-if evidence; finishes citing only the simulated record are refused until the error
limit; rereading sources exhausts the turn limit, mostly on rational. The teacher passed every check in 1 of 223
finished investigations. This is diagnosis only; it changes no result and selects nothing.
Revised after review the same day: the "no test warranted" labels were checked against the cases. For Aquaporin,
declining follows from dossier evidence (withdrawal of its offering, insolvency, bankruptcy order of 2 February 2026)
that no run of either arm ever read; all 11 finished trained runs recommend investing, so the failure is the search,
not a missing refusal. For Rational the label rests on the case author's judgement and is contestable. The teacher's
1 of 223 and the student's 1 of 48 come from different case distributions and show only that all-checks success is
rare in both. The improvement plan is reordered (justified propose-or-decline, balanced directional evidence linked
to the affected theory, recovery from simulated-only citations and from rereading), to be confirmed on development
cases before any new examples are selected; a future claim needs fresh evaluation cases, since these four companies
now informed the diagnosis. The frozen scores stand.

## 2026-11-08: public repository and release policy

At Hatem's request the code is public at https://github.com/HatemSaadallah/lexsi-strategy-agent (Apache 2.0), made by
`scripts/build_public_repo.py` from this repository: no history, no copies of the source papers (`papers/`,
`sources/`), every dossier excerpt cut to its first sentence of at most 25 words wherever it appears (Hatem's policy;
the agent's own exact-sentence quotes stay), and the cluster account, login host and home folder replaced by
placeholders. Its tests pass (206, plus the held-out digest test skipped, since the digest covers the full excerpts).
This repository stays private. The Hugging Face release (`scripts/build_release.py`, same redaction) waits for the team
organisation and Hatem's go.

## 2026-11-08: version 2 registered (`docs/V2_PLAN.md`)

A short continuation of the final adapter on 100-200 targeted single-decision examples (experiment design, belief
revision, evidence judgment, recovery), mixed with existing teacher rows at about 30% of supervised tokens, every target
passing a skill check fixed in code before generation. Development confirmed experiment design (4 of 7 finished runs),
evidence judgment (5 of 7 mislabel kinds) and recovery (3 of 8 unfinished reread); revision on directional evidence
could not be confirmed on development (3 such cases). Version 1 and its final-test result are untouched; a version 2
generalisation claim needs fresh held-out companies.
Revised the same day after an independent critique (a stand-in reviewer): reduced to
experiment design and refused-finish recovery, budget variants dropped (they cannot replay: `read_brief` returns the
budget), stricter gates on the new item only, a gentler mix (15-20% targeted, learning rate 2e-5 to 3e-5, about 100-150
steps), and a selection rule fixed in advance: 3 attempts x 15 validation cases for both versions, version 2 preferred
only at a mean-of-judges gain of at least +0.10 with a 95% lower bound above 0 and no more than 2 fewer finished of 45.
Timeboxed to three days; development result only. See `docs/V2_PLAN.md`.

## 2026-11-08: the experiment check misreads opposite predictions

Inspecting the version 2 gate on development outputs (Hatem's request) showed that the environment's experiment check
treats opposite comparisons as near-identical predictions, because it compares word overlap. Recounted, 5 of the 6
final-test runs it flagged "predictions barely differ" predict opposite outcomes (development: 1 of 2 and 3 of 4).
The frozen final-test numbers are unchanged and reported as computed; the diagnosis and article now say five of six
predictions-overlap failures involved contrasting predictions the checker treated as identical, which does not
establish that those experiments were otherwise sound. The version 2 gate recognises opposite comparisons (`targeted.mirrored`) and
two-branch decision rules; on development outputs it now keeps 12 of 17 proposals, and the rejections inspected were
identical predictions or rules without a number or second branch. Launch settings: the teacher's recorded reasoning
budget of 512 tokens and prompt version teacher-v2, 4 slots, as in collection.
The comparison test in the version 2 gate (`targeted.mirrored`) is a heuristic for structural screening only: it
recognises swapped terms without reading direction, so "A is lower than B" against "B is higher than A" (the same
outcome) can pass as different. Accepted examples are therefore inspected in a sample for substantive
discrimination; the aim is better teacher actions, not a higher acceptance rate. Version 2 is evaluated with the same
checks as version 1, and checker changes are reported separately from changes in model behaviour.
Version 2 teacher job 746017 died at start (exit 13, SIGPIPE): `nvidia-smi | head -1` under `set -o pipefail`, where
`head` can close the pipe before nvidia-smi has written everything; earlier jobs escaped the race. Found with a traced
debug job (746087 passed, 746088 reproduced it); fixed by reading the first line with awk (9924355). The teacher was
resubmitted as job 746091 with the recorded collection settings (reasoning budget 512, teacher-v2, 4 slots); the queued
batch was untouched.
Version 2 narrowed to experiment design (Hatem, 2026-11-08): 81 of the 82 collected states are at the test step and
only 1 is a refused simulated-only finish, which rarely occurs on training companies. `docs/V2_PLAN.md`, third revision.
Job 746091 then downloaded the model but its server never started: it was submitted without `NAME`, which the script
needs for its log files under `set -u` (earlier teacher jobs set it). Resubmitted with NAME=capv2; settings unchanged.
First version 2 teacher batch (746123, 28 states): 28 valid answers, **0 accepted**. Two errors of mine, not of the
teacher: the states were the student's first call in the test stage, where it was still reading sources (24 of 28),
and the teacher was given the loop-recovery instructions ("do not move to a later step before the evidence is in
place"), so it chose `read_source` in 26 of 28. Fixed (238781f): states are taken where the student itself proposed or
declined its test (53 states on 36 companies, plus the one recovery state), and the teacher gets experiment-design
instructions (`targeted.EXPERIMENT_ASK`). The rejected answers stay in the manifest. Job 746123 was cancelled before its
second batch, which had the same flaw; the teacher was relaunched as job 746236.
Version 2 examples under review (Hatem, 2026-11-08): the 17 accepted are exported with their exact states, source
dates, raw teacher replies and acceptance reasons (`reviews/v2_examples/`). Three independent language-model reviewers
assess them against Hatem's criteria; their assessments are **advisory
only**, and every keep or drop decision is Hatem's (no model selects training data). Training is paused
until that review. The 37 rejections each have exactly one reason; an earlier summary of mine miscounted them as 38.

## 2026-11-08: tool fields cut at 240 characters (found by the version 2 reviews)

The tool schema caps short text fields at 240 characters (`_TEXT` in `agent/runner.py`), and generation constrained by
that schema stops the text at the cap mid-sentence. In version 1's training data, 132 of the 158 `propose_test` targets
have a `decision_rule` at the cap (and 108 a `method`), so the model was trained on decision rules that are mostly cut
off; on the final test 23 of the trained arm's 37 accepted test proposals have a rule at the cap. This is a data-quality
limitation of version 1 and a plausible contributor to its weak experiment-design and recommendation scores; it does not
change any frozen number. The version 2 gates passed truncated rules, and 15 of the 17 accepted version 2 examples have
one. A future version needs longer limits for these fields (or a rule that must be complete) before any data is made.
Hatem chose one documented fix-and-regenerate round for version 2: longer limits for the test-design and reasoning
fields, teacher instructions that ask for mechanism-separating tests, proportionate and complete rules and staying inside
the case's time, three structural gates (complete rule, no pre-1995 online method, no source dated after the case), each
of the same 54 states asked once, and Hatem's review before any training. Details in `docs/V2_PLAN.md`, fourth revision.

## 2026-11-08: the rereading loop, fixed two ways (Hatem chose both)

A manual Try it run stalled at the test step rereading the same sources until the turn limit, the failure seen in 9 of
48 final-test runs; in 36 of 122 version 1 runs on training cases the model also reread a source a third time in the
test stage. The test stage offers the reading tools besides propose_test, and a reread is never refused.
- **Model:** the 35 distinct states where version 1 first reread a source a third time in the test stage (training
  companies, 27 of them) are added to the version 2 round as experiment-design states (origin "reread"): the teacher
  answers each once under the same instructions, the same gates apply, and Hatem reviews them with the rest.
- **Environment:** an opt-in reread limit (`Investigation(reread_limit=)`, runner `--reread-limit`) refuses a third
  read of one source, saying its text is already in the state. It is recorded in each episode's settings, so every
  earlier episode replays unchanged. Try it uses it by default (REREAD_LIMIT=2) and says so on the page. It is a
  harness change: version 1's reported results stay as evaluated, and any dev comparison runs both versions under the
  same setting, reported separately from model changes.
- Fixed with it: the tool refused a method or decision rule over 600 characters while the schema now allows 900, so
  in the running round answers between 601 and 900 characters are refused by the tools. The tool now accepts 900
  (old runs never exceeded 240, so replay is unaffected), and the round's answers are re-checked offline with the fix:
  the same single answers, no new sampling.
Try it's turn budget is raised from 45 to 60 (MAX_TURNS, labelled on the page; Hatem's suggestion). Of the 9
final-test runs that hit 45 turns, 8 were rereading, which the reread limit now stops, so the extra turns go to real
steps after a correction. A harness change like the reread limit: version 1's results stay at 45; for the version 2
development comparison the setting is fixed before it runs, and both versions run under it.
Try it gains a **live web research** toggle (Hatem, 2026-11-08), experimental and never part of an evaluation: a
`LiveDossier` (`env/live.py`) replaces the fixed dossier with DuckDuckGo search (the `ddgs` package), every result page
is fetched once and saved as a snapshot (URL, retrieval time, sha256 of the text, the excerpt shown), and quotes are
checked against that excerpt. Pages on the company's own site are company claims; other pages get a new class,
`web_page`, which says no analyst checked them. Live runs are never cached and are marked in the history and the label.
Checked end to end on the laptop: four live searches, six live pages read, sixteen snapshots saved.

## 2026-11-08: the offline re-check of the round's answers

`targeted regate` judges saved teacher replies again with the current code and samples nothing: every reply is
re-judged, including those the old 600-character tool limit refused, and each answer keeps its `decision_at_generation`
next to the new decision. Training rows are still made only from answers kept after the re-check and Hatem's review.
Tried first on the earlier batch (54 answers, 17 kept then): 1 is kept now. Of the 16 no longer kept, 15 fail the new
complete-rule gate (rules stopped at exactly 240 characters by the old schema) and one proposes an online method in a
case set in 1983; four answers rejected then are rejected now for the incomplete rule instead (20 decisions changed).
The one still kept showed a hole: its rule was cut at 240 characters right after "p<0.", which ends in a full stop.
Constrained generation stops a field exactly at its schema limit, so a new gate (`cut_off`) refuses any prose field of a
test, or any of the teacher's reasoning fields, that is at its limit, or at exactly 240 characters (the limit the first
batches were made under; an answer written to 240 by chance is lost, which is accepted). With it, none of that batch
is kept: 18 cut rules, 2 cut samples, 1 cut measure. The gates only confirm what the reviews found; that batch is not
used. The new round's answers are exported in full for Hatem's review by `scripts/v2_review_export.py` (the flags in
it are keyword aids, select nothing, and Hatem's choice is recorded in its `keep` field).
Third batch (54 states, the round's experiment states): 53 valid replies, 1 request timeout; 5 kept at generation, 18
refused only by the old 600-character tool limit. After the offline re-check, 5 are kept: 4 of the 5 (one has its
"learned" field cut at 700 characters) and 1 the old limit had refused. The case-date pattern of the in-period gates
knew only "It is [early/mid-/late] YEAR" and missed 16 dated cases ("It is March 2016", "It is March 1991", "It is
spring 2021"); it now reads them, and the re-check was run with it (the kept set did not change). The five are in
`reviews/v2_round2/targeted3_kept_for_review.md` for Hatem's decision.

## 2026-11-08: development comparison of the environment fixes (recorded before the runs end)

Version 1 (the final adapter, compact prompt) on the 15 development cases, 3 attempts each (45 runs per configuration),
code 1303fca / 9c30e1a, one GPU job per configuration:
- **as evaluated** (747625): 45 turns, 4 refusals in a row, no reread limit, no source dates, no stuck help;
- **fixed** (747626): 60 turns, reread limit 2, source dates in the state, stuck help after two refusals in a row;
- **fixed + weigh 3** (747636): the same, and each theory needs 3 weighed sources (or as many as were read) before
  the investigation moves on.
Measured mechanically on every run: finished, stop reasons, refused calls, sources weighed per theory, and the
confidence score out of five. Rule, fixed now: a configuration replaces the one before it in the Strategy Lab if it
finishes more runs and does not lower the mean confidence score; ties keep the simpler one. These are environment
changes, reported apart from any model change, and never applied to the reported final test. Blind judging of the
winner against "as evaluated" is optional and would use the frozen judge configuration.
Confidence on the final test's 28 finished runs, under the score out of five: 24 at 2/5, 2 at 3/5, 2 at 4/5 (no High).

## 2026-11-08: version 2, third teacher round (recorded before running)

After three advisory reviews found template answers in the second round (none of its 5 kept answers sound):
- **Instructions** (EXPERIMENT_ASK, third revision): test arms must differ in the product, its price or how it is sold,
  with the presentation otherwise the same (a message-only test needs a same-price control); the currency and methods of
  the case's time; each source shows its date (source dates in the state), only sources dated on or before the case,
  named by id; both theories kept credible; every outcome of the rule leads to a bounded next step.
- **Checks** (screens, so kept answers are still inspected): message-only arms with no product or price difference and
  no control; a rule that jumps to developing a product line with no bounded step; euros before 1999. On the second
  round's 5 kept answers they refuse Cree, Embrace and Black & Decker.
- **New skill, weigh**: the 81 states where version 1 left the weighing step after at most one source per theory with
  three or more real sources read, replayed with min_assessed 3 so the state asks for more; the teacher weighs one more
  source (assess_evidence, a read source, no repeat).
- **States**: 170 from version 1's runs on training companies (48 companies): 53 test design, 35 rereading, 81 weigh,
  1 recovery; all with source dates.
- **Sampling**: 2 answers per state at temperature 0.7; the code checks keep the first that passes, so at most one row
  per state; every answer is hashed into the manifest.
- **Server**: Command A+ Q4_K_M, 2 slots of 12,288 tokens (so the model fits on the GPU instead of offloading to the
  CPU, the cause of the earlier 1.5 tokens per second), prompt version teacher-v3.
Rows train only after Hatem's review. Cut-off as agreed: without about 60 approved examples by 11 November, version 2
stops and version 1 stays the submission.
Hatem's review of the second round (2026-11-08): of the 6 answers still passing every check, kept Superior and
Technogym; dropped Andis, Cotral, ARRI and Hilti. Two reasons in the pasted notes were corrected beside them (the
600-character refusal was the environment bug since fixed). The screens then had three holes, now closed: a single
price for the whole test counted as a price difference; "develop ... propositions" in the plural slipped past; and a
"pilot launch" of a product line or sub-brand counted as bounded. With them closed the screens agree with all six of
Hatem's decisions; they were tuned on these six, so this is a consistency check, not evidence that they generalise.
The third round's answers are re-checked offline with these screens before review.
Result (2026-11-08, 45 development runs each, rebuilt offline from the saved episodes because the job's AuditKIT step
failed on the new stuck_help setting; replay now passes the environment only the settings it takes):
- as evaluated (747625): 24 finished, 17 repeated refusals, 4 turn limit; 294 refused calls (245 repeats, 35 misquotes);
  mean confidence 2.21 of 5.
- fixed (747626): 23 finished, 22 repeated refusals, 0 turn limit; 350 refused calls (334 repeats, 7 misquotes); mean
  confidence 2.17.
Under the rule, "fixed" does not replace "as evaluated": it finishes one fewer run and does not raise confidence. The
reread limit turned rereading loops into refused calls, which end runs after 4 in a row, and stuck help did not rescue
enough of them. Misquotes fell from 35 to 7 (source dates in the state are the likely cause; not separately tested).
A fourth configuration, recorded before it runs: **dates + help** (60 turns, source dates, stuck help, no reread limit),
same 45 runs and rule, code b021891.

## 2026-11-08: test set 2, frozen before any run

Why: the final test's four companies support only a limited claim and have since informed the diagnosis, so a new claim
needs new companies (Hatem: "we need more data").
- **Companies (12)**, researched from public sources by four research agents and admitted only through our verifier
  (each quote found word for word on its live page): Ansell, Belimo, Drägerwerk, Franke Coffee Systems, Hach, Hoshizaki,
  Kingspan, Laerdal Medical, Mettler-Toledo, Tennant, Testo, Winterhalter. 221 verified records (14 dropped: 10 pages
  unreachable or blocking, 4 quotes not found). Each company: a base case and an irrelevant-what-if case, 24 cases;
  supporting and undermining what-ifs were not written for them. All marked test warranted. Premise records filtered to
  verified ones; Dräger's three missing premise records are replaced by its one verified company record.
- **Separation**: `data/dossier/cases_heldout2.json`, split `heldout2`; development and the final test cannot see its
  evidence (tests/test_test2_freeze.py); frozen digest 4db90205... in `docs/test2_freeze.json`. The final test's digest
  is unchanged (dce26d4f...).
- **Arms**: base (Tiny Aya bf16, staged prompt, no adapter) and version 1 (the final adapter, GGUF 41794b57..., compact
  prompt), exactly the final test's settings: context 12,288, 520 tokens per turn, 45 turns, 4 refusals in a row,
  temperature 0 with 0.4 only on a retry; 3 attempts; 144 runs. A version 2 adapter may be added as a third arm only if
  it is adopted on development by 11 November under its own rule, run with the same settings, and before any per-case
  look at test set 2; no failure analysis of test set 2 happens until every arm has run.
- **Judging**: the frozen judge package and configuration (judge-v1-two-backends-2). Claude now; Codex from 11 November
  (unavailable until then). Primary result: version 1 minus base, mean of the two judges, paired by case and attempt,
  95% case-cluster bootstrap (4,000 resamples, seed 20261106). A Claude-only result may be reported earlier, labelled as
  such. Also: each judge, each company, base against irrelevant what-if, finished counts and the mechanical measures.
- **Reporting**: both test sets side by side, test set 2 never pooled into the frozen final-test result.
Deviations, 2026-11-08 evening: the third teacher round's first job (747708) failed before any answer (the server,
without the rebuild flag, crashed with a CUDA error on its first requests; 0 of 340 requests answered). It was
resubmitted (747857) with the llama.cpp rebuild and 1 slot of 12,288 tokens instead of 2, because 2 slots still did not
fit on the GPU; instructions, states, checks and sampling are unchanged. The "dates + help" development job (747811)
was cancelled to free the GPUs for test set 2 (747855 version 1, 747856 base) and will be resubmitted unchanged.
Result of the third configuration (747636, 45 runs, rebuilt offline from the saved episodes): **fixed + weigh 3**
finished 25 (19 repeated refusals, 1 context limit), weighed 4.69 sources per run (3.29 as evaluated), mean confidence
3.12 of 5 (22 runs at 3, 3 at 4, none at 2). Under the rule it replaces "as evaluated" in the Strategy Lab: it finishes
more and raises confidence. Caveats: one more finished run of 45 is within noise, and part of the confidence rise is
built in, since one of the five checks counts three weighed sources, which the setting now requires. The Strategy Lab
now runs with source dates, the reread limit, stuck help and three weighed sources per theory. The frozen final test and
test set 2 keep the evaluated settings.

## 2026-11-10 01:40: test set 2, Claude-only result (frozen protocol unchanged; Codex from 11 November)

Claude judged all 133 packets (144 runs, 72 per arm) under the frozen judge-v1 package. Labelled Claude-only; the
primary result (mean of both judges) waits for Codex. Never pooled with the final test.

| | base (staged prompt) | version 1 (final adapter) | version 1 minus base, paired, 95% case-cluster bootstrap |
|---|---|---|---|
| Claude | 0.48 | 0.89 | **+0.41 [0.24, 0.57]**, 72 pairs, 24 cases |

10 of 12 companies positive (Mettler +1.00, Kingspan +0.89, Tennant +0.81, Ansell +0.57 … Dräger +0.16); Franke Coffee
−0.17 and Hoshizaki −0.15. By dimension (version 1 against base): problem framing 1.88 vs 1.03, revision 1.00 vs 0.11,
distinct theories 0.92 vs 0.40, recommendation 0.44 vs 0.03, experiment design 0.50 vs 0.22, evidence judgement 0.39
vs 0.28. Mechanical: finished 32 vs 2 of 72; passing every check 4 vs 1. The effect is smaller than on the final test
(Claude +0.64 [0.51, 0.77]) and evidence judgement and experiment design stay low, the weaknesses the corrective
families target.
Infrastructure: the Mac's network dropped during the first pass (108 connection errors, 1 timeout, 3 refused by the
ledger cap because of the held reservations); as for the final test, those attempts were archived
(`reports/judge/test2/claude_test2_archived_infra/`) and only they were judged again, never a valid judgment; two
later timeouts were retried once. The unbilled reservations of the 108 connection errors were released in the ledger
with a note. Actual cost $11.44 (approved about $10).

## 2026-11-10 03:55: corrective pilot 1 result, instructions changed for pilot 2
Pilot 1 (job 750511, code 1e00c09, 51 states from training companies): 15 kept, all 15 rebuild from the manifest and
today's replay. Per family kept/asked: numbers 0/10, experiment 1/10, classify 2/10, unstick 2/10, simulated 0/1,
revise 10/10. Main causes: 11 of 30 numbers/experiment/classify answers made a different call than the state is about
(mostly read_source); 11 answers named no id from the state; 4 finishes cited sources read but never assessed; 3 tests
again varied only the message. Two of the 5 non-revise kept answers are weak on inspection (cotral unstick: why_next
says add a theory, the call reads a source; arri experiment: a message survey), so review stays necessary.
Changes (5b8f271), gates unchanged: the teacher is offered only the tools of the decision the family is about (finish;
propose_test/decline_test; assess_evidence), every family is told to write exact ids and act on one it names, the
finish instruction says only assessed sources count and no numbers in a next action without a proposed test. Pilot 2
(job 750894): 32 states not used in pilot 1, 8 each of numbers, experiment, classify, unstick; revise is dropped from
pilots because the student already passes its gate (22/22). The full batch waits for pilot 2.

## 2026-11-10 11:05: corrective pilots 2 and 3, export for review
Pilot 2 (750894, 5b8f271, 32 states): 9 kept (unstick 6/8, classify 3/8, numbers 0/8 with 6 citing unassessed
sources, experiment 0/8). Pilot 3 (751211, 528dc19, 24 states): 7 kept (numbers 4/8, experiment 1/8, classify 2/8).
Pilot 3 numbers rejections are real invented figures (a "$25" price floor, ages 25-55); experiment rejections are
mostly fields cut at the length limit (4 of 7). Classify stays low because the evidence-kind annotation is inconsistent
for press articles (the same kind of trade article is market_fact in one case, customer_observation in another), so a
correct reading can fail; the check and annotations are frozen and unchanged, noted for a later audit. The
review exporter now re-judges corrective answers by their own family gate (it had used the round-3 gate). 31 kept
answers from 107, all passing provenance, replay and split, are on the Review page (reviews/v2_round4). Nothing trains.

## 2026-11-10 19:30 UTC: a hosted teacher (DeepSeek) for the corrective families, and an LLM reviewer (registered before any result)
Why: the V2 stop decision (V2_CORRECTIVE_PLAN section 10) is a finding about the teacher. Command A+ made the student's
own errors (evidence kinds, dates, message-only tests) and could not write a sound experiment design in two attempts.
Hatem asked to try a stronger teacher, and to build on version 1 rather than start again.

**Teacher.** DeepSeek V4.1-Flash (API model `deepseek-flash`, DeepSeek-V4.1-Flash-1017). The weights are MIT, and
DeepSeek's Open Platform terms allow using outputs to train other models, distillation included (copy of the terms in
`docs/terms/`). Called through `pipeline/hosted_teacher.py`, a separate entry point. The corrective pipeline's states,
families, instructions and gates are unchanged (`pipeline/corrective.py` at this commit). The evaluated runner, the
Strategy Lab and the Command A+ jobs are unchanged.

Differences from the llama.cpp teacher, fixed now:
- Strict tool calling replaces the JSON-schema grammar. The reply is checked against the original schema, and up to
  two repair turns name the exact limits broken. A reply that still breaks them is refused, as a reply cut off by the
  grammar was.
- Thinking mode is on (the API default), with up to 16,000 tokens. The API takes no seed, so a rerun is not
  bit-identical; every reply is hashed into the manifest as before.
- Every request is logged with its model, fingerprint, usage and cost.

**States.** `experiments/v2_corrective/all_states_v3.json`: 244 states from version 1's runs on training companies
(unstick 69, experiment 53, classify 53, numbers 46, revise 22, simulated 1). One answer each. No development,
final-test or test-set-2 company, as before.

**Reviewer (Hatem's decision, replacing the human Keep/Drop review).** DeepSeek V4-Pro (`deepseek-v4-pro`,
DeepSeek-V4-Pro-0813). It is a different model from the teacher, and it reviews the exported examples with a written
rubric (`pipeline/hosted_review.py`, built from the earlier human reviews and section 9's criteria).

Qualification rule, fixed now:
- Before it reviews anything, it reviews the 6 examples Hatem decided (2 Keep, 4 Drop).
- It qualifies only if it agrees on at least 5 of 6 and keeps both of Hatem's Keeps.
- If it fails, the examples go to human review as before.
- Claude's advisory verdicts are not used, because Claude's output never decides training data.

How its decisions are recorded and checked:
- They are written as `review_source: llm`.
- A human decision is never overwritten.
- The model card and paper will say that the examples were selected by an LLM reviewer.
- A human spot check of 10 randomly chosen LLM keeps is recommended before training. If Hatem drops more than 2 of
  the 10, the LLM review is not used.

**What follows, unchanged from V2_CORRECTIVE_PLAN:**
- the threshold of section 9: at least 30 keeps in at least 3 families, with experiment design among them;
- the training mix of section 7, continuing version 1's adapter;
- the screen of section 8;
- the adoption rule of section 6.

The training job's approval file is created only by a human. Neither test set is used.

**Budget.** At most $10 of DeepSeek credit for this round. Each process stops at its own cap (`HOSTED_BUDGET_USD`).

**Later, not registered here.** About 200 new full investigations by the same teacher on training companies, if this
round shows the teacher is better. That will be registered before it runs.

## 2026-11-10 18:35 UTC: reviewer qualification result, and no human review (Hatem's decision, before any batch is reviewed)
Qualification (`experiments/hosted_teacher/reviewer_qualification.json`): DeepSeek V4-Pro agreed with Hatem on 4 of 6.
It dropped all 4 of his Drops, for the same reasons he gave, and also dropped both of his Keeps:
- Superior: the arms mix proposition with price (€45 against €55) and have no same-price control;
- Technogym: the variants differ in positioning only.

It is therefore **not qualified** under the rule registered above (at least 5 of 6, with both Keeps kept). Its errors
on this sample are all in one direction, dropping rather than keeping.

Hatem's decision: no manual review. The unqualified V4-Pro reviewer is used as a strict filter, unchanged:
- only examples it keeps can train;
- the rubric is not edited after seeing the qualification, and there is no human spot check;
- this replaces the human review and spot check registered above.

Disclosure, in the model card and paper: the corrective examples were selected by gates plus an LLM reviewer that
failed its qualification against human decisions, because it was stricter. The rest of the plan is unchanged: section
9's threshold, section 7's mix, section 8's screen and section 6's adoption rule. The training job's approval file is
created on Hatem's explicit instruction.

## 2026-11-10 18:30 UTC: a second hosted teacher, DeepSeek V4-Pro, on the same 244 states (Hatem's decision, before any result)
The same entry point, states, instructions, gates, repair turns and reviewer as the V4.1-Flash round, with
`HOSTED_MODEL=deepseek-v4-pro` (DeepSeek-V4-Pro-0813). It runs until the credit runs out. States not answered for
lack of credit are reported as such and never filled in.

The reviewer stays V4-Pro with the rubric unchanged, so both teachers are filtered alike. For the Pro answers this is a
model reviewing its own model's answers; that is disclosed. Comparison: on identical states, the share kept by the
gates and then by the reviewer, per family, for Command A+ (pilots 1-4, regated by today's gates), V4.1-Flash and
V4-Pro. Where both DeepSeek answers to one state are kept, the Pro answer is used (the stronger model, fixed now).

## 2026-11-10 18:55 UTC: a second shortening turn for experiment answers refused only for length (before it runs)
Flash's experiment family: 0 of 53 kept, and 20 of them were refused only because a field was still over its limit
after experiment_design's single shortening turn. Pro's experiment family shows the same pattern so far.

The change (`hosted_teacher.py reshorten`):
- Applies only to answers refused with "still over the length limit after one shortening".
- The same conversation gets one more turn with the exact counts (experiment_design.shorten_note), so the shortened
  text is still the teacher's own.
- That reply goes through the same compose, limits and family gate as before. Every reply is hashed into the manifest.
- Every other refusal stands. No answer is rewritten by code.
- For both teachers. The answers kept this way go through the export checks and the same reviewer.

## 2026-11-10 19:05 UTC: the experiment family is judged by the reviewer, not by the keyword screens (before it runs)
The keyword design screens refuse sound designs. Example: Pro's Sealed Air answer, a same-price test of poppable
against pop-less wrap (a real product attribute), refused as "differs only in wording". Nour's plan already noted that
these screens have errors of their own (V2_CORRECTIVE_PLAN section 6).

**What changes, for the experiment family only** (`pipeline/hosted_experiment.py`):
- These screens no longer decide: targeted.gate_mechanism, gate_test and gate_decline.
- An answer goes to the unchanged DeepSeek V4-Pro reviewer if it passes the mechanical checks:
  - the call is accepted and grounded;
  - no field is cut off or over its limit;
  - it stays inside the case's period and currency, and cites no later source;
  - it proposes or declines as the case's own `test_warranted` says;
  - it is from a training case;
  - its replies are in the manifest, and its composition rebuilds.
- The reviewer's rubric already drops message-only tests without a same-price control, non-discriminating predictions,
  jumps to a launch, trivial commitments and declines that contradict themselves.

**Which answers:** Flash's and Pro's experiment answers. Where a state has a second-shortening answer, that one is used.

**What stays the same:**
- Every other family keeps its gate.
- The evaluation's `experiment_v2` measure (V2_CORRECTIVE_PLAN section 6) still uses the screen, unchanged and the
  same for both arms.

## 2026-11-10 19:15 UTC: the DeepSeek round's result, the threshold met, and v2 training (Hatem's instruction to train on top of v1)
On the 244 states, the DeepSeek V4-Pro reviewer kept (Command A+'s 27 gate-passed pilot answers, reviewed alike: 4):

| Teacher | Main families | Experiment | Total |
|---|---|---|---|
| V4.1-Flash | 67 | 4, of 10 passing the mechanical checks | 71 |
| V4-Pro | 78 | 8, of 15 passing the mechanical checks | 86 |

Both teachers often declined tests the case warrants: Flash 18 times, Pro 19.

**Training rows:** where both DeepSeek teachers have a kept answer for the same state, Pro's is used (48 Flash keeps
superseded). This gives 109 approved rows, all rebuilt exactly from the manifests.

**Continuation set** (`scripts/v2_training_set.py`, unchanged):
- 105 corrective rows (numbers 9, classify 18, unstick 56, revise 10, experiment 12; 1 duplicate dropped, revise
  capped), each presented twice;
- 1,707 of version 1's own rows;
- 411 validation rows;
- a corrective share of 0.20; output sha256 4e06896d.

**Threshold (section 9):** met. At least 30 keeps: 105. At least 3 families: 5. Experiment design among them: 12.

**Training:** `jobs/train_v2_corrective.sbatch` unchanged. It continues version 1's adapter, one epoch, learning rate
2.5e-5, seed 7. The approval file is created on Hatem's instruction ("train on top of command A+"). Then the section 8
screen and the section 6 adoption rule. Version 1 stays the submission unless v2 passes them.
Jobs (2026-11-10, code 6c9b182):
- v2 training: 752833.
- Section 8 screen: 752835 for V1, 752836 for V2, the latter after 752833 succeeds.
- Both screen arms: the 15 development cases, one attempt, the compact prompt, the as-evaluated controller,
  SKIP_BASE=1 and DIAGNOSTIC=1 as for the final test.
Infrastructure retry (2026-11-10 19:25 UTC): screen arm 752835 failed before any episode because the code copy lacked
`data/dossier`. I had shipped only src, jobs and scripts. The case files of the same revision were added, and V1 was
resubmitted unchanged as screen_v1b. 752836 (V2) reads the same copy.

## 2026-11-10 22:40 UTC: v2 screen result, stopped under section 8; version 1 stays
Training 752833 completed: 480 steps, loss 0.61. Screen, 15 development cases, one attempt, the same code and settings:

| | V1 (752848) | V2 (752836) |
|---|---|---|
| Finished | 7 | 0 |
| Valid completion | 1 | 0 |
| Turn limit | 4 | 10 |
| Repeated refusals | 4 | 5 |
| Refused calls | 128 | 146 |
| read_source | 156 | 299 |
| Rereads | 64 | 186 |
| assess_evidence | 91 | 40 |
| propose_test | 8 | 0 |
| finish | 12 | 0 |

Section 8, condition 2 fails: V2 has 7 fewer finishes, against at most 2 allowed. **Stop: V1 stays.** The screen is the
reported result. It was not judged, because the rule does not need quality to decide this, and judging would cost
money without changing the decision.

Likely cause (post hoc):
- The corrective set was dominated by unstick (56 of 105), whose kept answers are mostly read_source.
- Each row was presented twice at 20% of the target tokens.
- So the continuation taught rereading over weighing and finishing.

Single-step corrections skew the action distribution in a way whole investigations do not. Any further DeepSeek data
should be whole investigations, or corrections balanced by action, registered before it runs.

## 2026-11-10 22:55 UTC: whole investigations by DeepSeek V4-Pro (Hatem's decision, registered before any run)
Why: single-step corrections skewed the action mix (V2's screen). Whole investigations carry the procedure's own mix.

**Teacher and runner:**
- DeepSeek V4-Pro (`deepseek-v4-pro`) through `pipeline/hosted_investigations.py`, which points the unchanged runner's
  chat at the hosted client.
- Teacher prompt, tools, stages and guards as for the Command A+ investigations: context 16,384, 2,000 tokens per
  turn, 45 turns, temperature 0 (the API takes no seed).
- The strict-schema conversion now also handles a tool with no arguments (placeholder) and a map keyed by ids (a list
  of key/value pairs, turned back before the original schema is checked).

**Cases:** the 111 training cases of version 1's rows (57 companies, no development company), at attempt 10, then 11,
and so on, so the seeds and labels differ from earlier runs. 16 investigations at a time.

**Budget:** Hatem's rule is to keep $5. The client reads the real balance every minute and refuses new requests below
$5 (`HOSTED_MIN_BALANCE=5`). An investigation cut off by the floor is recorded as a harness failure and never used.
The balance was $31.51 before the pilot.

**Pilot first:** 2 investigations, to check the pipeline and measure the cost per investigation.

**Rows** (registered now, applied after generation):
- The standard pipeline (`pipeline/rows.py`): replay-exact episodes, the same filters as version 1's rows.
- The hosted label's hash is added to `TEACHER_WEIGHTS` for this teacher only.
- Before any training:
  - the share of each action in the new rows is reported against version 1's;
  - a mix whose read_source share is more than 1.5 times version 1's is not trained.

**Training:** continue version 1 once, not twice. The new rows are at most 30% of target characters, with the rest
from version 1's rows. Then the section 8 screen and the section 6 rule, as for the first v2. Version 1 stays unless
the new adapter passes them.

## 2026-11-10 23:05 UTC: validation mixes both teachers (Hatem's request, before any DeepSeek investigation row exists)
The trainer's held-out loss currently uses only Command A+ rows from the six development companies.

The change:
- The DeepSeek investigations of six training companies are held out for validation only and never trained on:
  diatek, illumina, perrigo, resmed, sensirion and sievi. They were drawn with `random.Random(20261110)` from the 57
  companies in version 1's rows.
- Validation is then the development companies' Command A+ rows plus these companies' DeepSeek rows.
- Held-out loss is reported per teacher, so it shows whether the adapter fits each teacher's investigations, not only
  Command A+'s.
- Those six companies' Command A+ rows stay in training as before, so version 1's own data is unchanged.

## 2026-11-10 23:10 UTC: a universal held-out loss, and teacher-free selection (Hatem's request, before any DeepSeek investigation row exists)
A loss on one teacher's held-out text measures imitation of that teacher, not quality for a human reader. So:

1. **Monitoring.** The trainer's held-out loss is reported as one universal number: the mean of the Command A+ and
   DeepSeek validation losses, weighted equally, so neither teacher's style dominates. The per-teacher losses are
   reported beside it as diagnostics only. No loss selects or rejects an adapter.
2. **Selection** stays teacher-free, as in V2_CORRECTIVE_PLAN sections 6 and 8. An adapter is judged only by what it
   does on development cases:
   - the environment's checks: finished, valid completion, no invented numbers, `experiment_v2`;
   - the blind score on the frozen nine-dimension rubric, written for a human reader, from the qualified judge with
     the adapter hidden.
   No teacher text is involved.

## 2026-11-10 23:30 UTC: new training cases written by DeepSeek from verified public sources (Hatem: "generate more cases")
Claude may not author training data, and a case's question and brief are in every training row. So new training cases
are written by DeepSeek V4.1-Flash (`pipeline/hosted_cases.py`), whose terms allow training other models on its outputs.

**Steps:**
- DeepSeek proposes manufacturers absent from every dossier file, and from the same groups.
- Web searches (ddgs) return pages, fetched as the verifier fetches them.
- DeepSeek copies 8 to 12 exact quotes, with their metadata, and writes one or two sentences on what the company makes
  and for whom.

**What a case can contain:**
- The verifier admits only quotes found word for word on their live page, as for every dossier record.
- A company with fewer than 4 verified records is dropped.
- The question and the rest of the brief are the existing template, word for word.
- `add_cases --split training` adds the base case and its irrelevant-what-if variant.

**Excluded from every test:** these companies are training only, and neither frozen test set changes.

**Cancelled:** the third pass of investigations, so the leftover credit can write these cases. Their own Pro
investigations need more credit, kept above the $5 floor.
Implementation (2026-11-10 23:20 UTC), `training/train.py`:
- `--validation-rows` adds the held-out DeepSeek rows.
- Each validation row is grouped by teacher and company (`ds_` prefix for DeepSeek).
- `eval_loss` is then the universal loss, the mean of the two teachers' company-balanced means. It is logged with
  `eval_teacher_commanda_loss` and `eval_teacher_deepseek_loss`.
- The trainer's existing best-checkpoint choice within a run uses this universal loss. Adopting the adapter still
  depends only on the teacher-free screen.
- The split check compares case and teacher, so the Command A+ rows of the six companies stay in training.
- Without DeepSeek rows, behaviour is exactly as before (version 1 reproducible).

## 2026-11-10 23:25 UTC: all the data from both teachers (Hatem's decision, before any row is built)
Asked how much DeepSeek data to mix in, Hatem chose: "use all the data that is available from both". This replaces the
registered cap of DeepSeek at most 30% of target characters.

**The continuation:**
- every row of version 1's set (`rows/final.jsonl`; the six development companies held out for validation, as before);
- every replay-exact row of the DeepSeek V4-Pro investigations, except the six validation companies' DeepSeek rows,
  which validate only;
- one pass, continuing version 1's adapter, learning rate 2.5e-5, warmup 10%, seed 7;
- universal validation loss, as registered.

**Unchanged:**
- The action-mix check: the mix is not trained if its read_source share exceeds 1.5 times version 1's.
- The section 8 screen and the section 6 adoption rule.

**Compute:** about 7,500 to 8,000 rows. A full A100 (7g.80gb), a 12-hour limit, and checkpoints every 25 steps so a
stopped job resumes. Job script: `jobs/train_v3.sbatch`.

## 2026-11-11 00:05 UTC: generation ended, version 3 training submitted
**Investigations:** 288 DeepSeek V4-Pro investigations (216 on the old training cases, 70 on the new cases, 2 in the
pilot), 154 of them finished. Hatem stopped the run at that point ("ok enough").

**Rows** (`experiments/hosted_investigations/v3_rows_report.json`):
- 154 investigations accepted: every finished one replays exactly; 112 never reached an accepted finish;
- 3,611 training rows from 69 companies, and 262 DeepSeek validation rows;
- read_source share 1.16 times version 1's, inside the 1.5 limit;
- training rows sha256 a4845f4c, the same locally and on the cluster.

**Jobs:** training 753357 (full A100, code 1d725b1); screen arms 753358 (V1) and 753360 (V3, after training).

**Deviation:** the $5 balance floor was overshot by $0.48 (the balance ended at $4.52). Each process read the balance
only once a minute, and requests already in flight kept billing. The client now reads it every 20 seconds and stops
new work $1.50 above the floor.

## 2026-11-11 09:30 UTC: version 3 screen result, stopped under section 8; version 1 stays
Training 753357 completed: 1,876 steps in 4.7 h. Best checkpoint 1876; universal held-out loss 0.913 (Command A+
0.717, DeepSeek 1.110).

Screen: the 15 development cases, one attempt, code 1d725b1. V1 is 753358, V3 is 753360.

| | V1 | V3 |
|---|---|---|
| Finished | 7 | 7 |
| Valid completion | 2 | 1 |
| Repeated refusals | 6 | 8 |
| Turn limit | 2 | 0 |
| Refused calls | 125 | 68 |
| Mean calls | 35.0 | 23.6 |
| Finished runs failing no_invented_numbers | 2 | 1 |
| Finished runs failing evidence_classes | 1 | 5 |

Of V3's refusals just before it stopped, 24 of 32 were a repeated search ("you already ran that search").

Blind Claude judging (judge-v1 unchanged; 29 packets, all valid; run `claude_screen3`): V1 1.049, V3 0.832. V1 minus V3
is +0.217 [−0.178, 0.633] over 15 pairs. By company: Hellberg +1.01, Neumann +0.40, ACR +0.06, Deere −0.12, Tanita
−0.24, Jotun −0.99.

**Decision:**
- Condition 1 is met: fewer finished runs fail no_invented_numbers.
- Condition 2 fails: blind quality V3 − V1 = −0.22, below the allowed −0.10.
- **Stop. V1 stays the submission.** V3 is reported as a development result.
- No test-set-2 arm is run for it (its rule needed adoption on development by 11 November).

**Likely cause (post hoc):**
- The DeepSeek investigations had almost no refused calls, so V3 learned their direct style but not recovery; it
  repeats a refused search until the four-refusal stop.
- Its theories are also thinner: distinct theories 0.87 against 1.47.

**Infrastructure** (no judgment lost or repeated):
- The first judging attempt was refused by the run cap.
- The second was refused by the ledger, because its output folder name `claude` reused the final test's run purpose.
- Both archived; the valid run is `claude_screen3`.

## 2026-11-11: version 3 on both test sets, exploratory only (Hatem: "run v3 anyways and we include it in the paper")

Decided after version 1's results on both test sets were known, and after version 3 failed its development screen
(entry 09:30 UTC above). So these runs **select nothing**: version 1 stays the submission and its frozen results are
unchanged; the version 3 numbers are reported in the paper as a labelled exploratory comparison only.
- Arms: version 3 only (`runs/v3/adapter`, conversion gate passed on its screen: worst gap added 0.072), compact prompt,
  `SKIP_BASE=1`, `ATTEMPTS=3`, every setting as version 1's run on each set: final test with runner code d3aa608, split
  heldout, the 16 cases (48 runs); test set 2 with runner code 2e9cbbd, split heldout2, the 24 cases (72 runs). Context
  12,288, 520 tokens per turn, 45 turns, 4 refusals in a row, temperature 0 (0.4 only on a retry).
- Judging: the same frozen judge package and configuration (judge-v1-two-backends-2), Claude first, within the $60
  ledger cap (final test first, test set 2 if the cap allows); Codex later if available. Version 3's packets are judged
  alone and compared with version 1's existing judgments of the same cases and attempts; Claude-only results are
  labelled as such.
- **Judge change (Hatem: "you can use claude code for judging instead of the api"), before any version 3 output was
  judged:** a third backend, `claudecode` (the same model claude-opus-5-5, the same frozen judge prompt as its system
  prompt, effort medium, through Claude Code print mode on the subscription login; no tools, MCP servers, settings or
  sessions, an empty folder outside the repository). Added to `reviews/judge_v1/backends_v1.json` as version
  judge-v1-three-backends-3; the claude and codex entries are unchanged, so their receipts still bind. Qualified under
  the same scoring rule on the same 40 packets (`reports/judge/claudecode_score_qualification.json`: sound above flawed
  in 19 of 20 clusters, 17 needed; 1 invalid, 4 allowed). Because it is a different instrument from the API judge,
  base, version 1 and version 3 are all rejudged together, blind and shuffled, on each test set, and only those
  same-judge numbers compare the arms (version 1 minus base under this judge also checks it against the API judge's
  +0.64 on the final test). No API spend.

## 2026-11-11: repositories renamed to aemon; history rewritten without the Claude co-author line

Hatem: "rename the repo to aemon ... both public and private, and dont include claude in the contributors". The public
repository is now https://github.com/HatemSaadallah/aemon (was lexsi-strategy-agent) and the private one
https://github.com/HatemSaadallah/aemon-dev (was lexsi-ai-hackathon); GitHub redirects the old URLs. Every commit
message on every branch and tag of both was rewritten to drop tool-generated trailer lines, then
force-pushed. **File contents are unchanged; only commit IDs changed.** Earlier entries,
reports and run records cite the old IDs (for example the final test's runner code d3aa608, now 2fb09e7, and test set
2's 2e9cbbd, now 7e08754): `docs/history/commit_map_private.tsv` and `commit_map_public.tsv` map every old ID to its new
one. The old histories are kept as bundles outside the repository. Tags v1-freeze, v1-final-test and v1-test2 point
at the rewritten commits. Nour's clone needs `git fetch && git reset --hard origin/main` (or a fresh clone).
- **Result (exploratory; selects nothing):** base, version 1 and version 3 rejudged together, blind, by the Claude Code
  judge. Its version 1 minus base agrees with the API Claude judge's (final test +0.63 [0.48, 0.77] against +0.64;
  test set 2 +0.36 [0.19, 0.54] against +0.41), so the instrument change does not move the scale.

  | | base | version 1 | version 3 | version 3 minus version 1 | finished (v1 / v3) | every check passed (v1 / v3) |
  |---|---|---|---|---|---|---|
  | Final test (4 companies, 48 runs per arm) | 0.55 | 1.18 | 1.06 | -0.12 [-0.28, 0.03] | 28 / 37 | 1 / 3 |
  | Test set 2 (12 companies, 72 runs per arm) | 0.49 | 0.86 | 1.22 | **+0.36 [0.21, 0.51]** | 32 / 57 | 4 / 18 |

  On test set 2 version 3 is higher for 10 of 12 companies (Mettler -0.06 and Tennant -0.09 the exceptions) and on 8
  of 9 dimensions (not framing), and it makes half the refused calls (305 against 584). On the final test the gap is
  Aquaporin (-0.46); the other three companies are within 0.14. No version 3 run found Aquaporin's insolvency either;
  all 9 finished runs recommend investing. One version 1 packet on test set 2 (ansell-base) was judge-invalid and is
  reported missing. Reading: the development screen (6 companies, one attempt, 15 runs per arm) said version 3 was
  worse; the larger test set 2 says it is clearly better, and the final test cannot tell them apart. The screen was
  too small to decide. These numbers come after both test sets were used for version 1 and must be reported as an
  exploratory comparison; under the frozen plan version 1 remains the submission.

## 2026-11-11: adapter switching mid-run, development only (Hatem: "i like the idea of switching the adapter mid run ... do that and test it")

Fixed before any run. One llama.cpp server holds both gated adapters (version 1 as id 0, sha256 41794b57...; version 3
as id 1, ea919380...), and `runner --lora-route` picks the adapter for each turn from the stage and from the count of
refusals in a row the runner already keeps (new `stuck=ID`, `stuck_after=N`, default 2; it never sees a judge or the
case). Job `jobs/eval_switch.sbatch`; every arm on the same two-adapter server, compact prompt, 45 turns, 4 refusals in
a row, temperature 0 (0.4 on a retry), the 15 development cases on the 6 validation companies, **3 attempts** (45 runs
per arm; the 1-attempt screen was too small).
- `v1`: default=0. `v3`: default=1 (the single adapters, rerun on this server so every arm matches).
- `v3_rescue`: default=1,stuck=0 (version 3; a stuck turn goes to version 1).
- `v1_rescue`: default=0,stuck=1 (version 1; a stuck turn goes to version 3).
- `dig_then_reason`: default=1,brief=0,frame=0,evidence=0 (version 1 gathers evidence, version 3 does the rest).
Judging: the Claude Code judge (claudecode receipt), all five arms in one blind shuffled packet set. Reported: each
switching arm minus v1 and minus v3, paired, case-cluster bootstrap; finished runs; refusals; how often each adapter
wrote a turn. These are development numbers: they can choose a routing rule to test, never a submission. A claim
needs a test on companies neither test set used.

## 2026-11-11: company status check (Aquaporin), and a teacher run with it (Hatem: "yes do it, also ... run the teacher particularly for this")

Diagnosis, before any change: across all 144 Aquaporin final-test runs (base, version 1, version 3) the insolvency
records never appeared in a search result; every query was about the market question. Plain queries ("Aquaporin
company", "Aquaporin news 2026", "Aquaporin risks") return them in the top three. So the agent never looks at the
company's own position, and neither did the teacher it learned from.
- **Environment, opt-in `status_check`** (recorded in each episode's settings; episodes without it replay unchanged):
  a tool `company_status {}` returns the company's three most relevant records for one fixed query (its name plus
  words for a change of position: results, insolvency, bankruptcy, acquisition, profit warning, restructuring,
  funding, ...), dated ones first, newest first; it uses no search. Stages `status` (only company_status open) and
  `status_reading` (read one of its results) come right after framing. `finish` must cite a status source it read.
- **Aquaporin diagnostic** (labelled: Aquaporin is a test company, so this shows whether the fix works on the known
  failure and is no test result): version 1 and version 3 with the status check on the 4 Aquaporin cases, 3 attempts.
  Measured mechanically: runs that read an insolvency record, runs that cite it in finish, finished runs, and runs
  whose recommendation still says to invest without naming the insolvency.
- **Harm check, development:** version 1 and version 3 with the status check on the 15 development cases, 3 attempts,
  on the two-adapter server, compared with the `v1` and `v3` arms of the switching test (same server, cases, attempts),
  judged blind by the Claude Code judge.
- **Teacher (Command A+, through the same environment, status check on):** the 93 base cases of the training companies
  (the 6 validation companies and all test companies excluded); first the 17 whose status results carry a change of
  position (portwest, zarges, masimo, arri, nilfisk, tupper, microban, orasure, illumina, stihl, maglite, sma, osram,
  martek, perrigo, searle, lmericsson) at temperature 0 and again at 0.4, then the other 76. Rows only from episodes
  that replay exactly and finish accepted, as before. No Claude output is used.
Fix, 17:30, before the teacher run started (job 754912 held, then cancelled and resubmitted): with the status check,
the status sources counted toward the evidence stage's minimum of 3 sources read, so runs read the status results,
went to the theories stage with no market search, and looped on repeated searches (v1 Aquaporin: 117 repeat refusals in
12 runs; development: 1 of 15 and 0 of 12 finished before the jobs were stopped). Status sources now do not count
toward that minimum and are not offered as evidence-stage reads. Runs without the status check are unchanged. The
Aquaporin diagnostic above ran before this fix and is rerun with it; the development check is rerun too.

## 2026-11-11: adapter switching, development result (Claude Code judge, 207 of 207 packets valid, 45 pairs each)

Mean score (0 to 3) and finished runs of 45: v1 1.06 (24), v3 0.86 (19), v3_rescue 1.17 (33), v1_rescue 1.20 (26),
dig_then_reason 1.24 (33). Paired, 95% case-cluster bootstrap: dig_then_reason minus v1 +0.17 [0.02, 0.35], minus v3
+0.38 [0.13, 0.62]; v1_rescue minus v1 +0.13 [0.03, 0.24]; v3_rescue minus v1 +0.10 [-0.15, 0.38], minus v3 +0.31
[0.08, 0.54]; v3 minus v1 -0.20 [-0.53, 0.11]. In v3_rescue, version 1 wrote 102 of 1,392 turns (7%) and stepped in on
37 of 45 runs. Development numbers on 6 companies: they choose dig_then_reason (version 1 for the brief, frame and
evidence stages, version 3 after) as the routing rule to test on companies neither test set used; they are no test
result, and version 1 stays the submission.
Second fix, 17:55, before the teacher started (755028 held, then cancelled and resubmitted): on the development
companies, `finish` was refused for not citing a status source, because the fixed query's words matched other
companies' records (for Hellberg, 3M's annual report and sales), which a run reasonably does not cite; runs ended on
repeated refusals. On Aquaporin the same rule was met by appending the bankruptcy record's id without a word about it.
Now: status results keep only records that name the company (falling back to the best matches if none does), and
`finish` takes a required `company_position` text instead (the company's current position and how it bears on the
recommendation), which the grammar always lets the model write. The two status-check runs on the earlier rule were
stopped; the diagnostics are rerun on this one (status3_*).

## 2026-11-11: CuratorKIT row curation and an Unsloth smoke test, for version 4 only (Hatem: "yes")

- **CuratorKIT** (`aemon.rows.curate`, `CURATE=1` in `jobs/train_after_teacher.sbatch`): CuratorKIT decides which rows
  to keep and never rewrites one (kept rows are the original lines). Exact deduplication on (state, target call),
  since CuratorKIT's default key (instruction + output) on the target alone would merge one call made in different
  states; MinHash off, because consecutive turns of one investigation share most of their state; its secrets gate on
  with the hex-entropy detector off (7 false positives on hashes in v1's rows). On v1's rows: 4,302 -> 3,958, all 344
  dropped rows exact duplicates (172 the identical first read_brief). Applies to version 4's rows only; v1 and v3 are
  unchanged.
- **Unsloth** (`--unsloth`, `jobs/unsloth_smoke.sbatch`): Unsloth 2026.11.3 needs transformers <= 5.17, TRL 1.15 and
  torch 2.14.1 against the project's 5.22.1, 1.7.1 and 2.11, so it runs in its own environment. Smoke test: the same
  50 rows, LoRA, seed and 12 steps, trained through AgentTune both ways; compared on loss per step, seconds, peak
  memory and GGUF conversion. Version 4 trains with Unsloth only if its losses track the current trainer's and its
  adapter converts and passes the conversion gate; otherwise it trains as v1 did. Either way the software stack is
  recorded with the adapter, since a different stack is a difference between v4 and v1 beyond the data.
Unsloth smoke result (job 755202, 2026-11-11 18:56; Unsloth 2026.11.3 with torch 2.11, transformers 5.17, TRL 1.7.1 and
AgentTune and AuditKIT at the lock file's commits): the same 50 rows, LoRA, seed and 12 steps. Losses track the current
trainer to within 0.007 at every step (first 1.2156 against 1.2145, last 0.8944 against 0.8907); both adapters convert
to GGUF (60,491,936 bytes each). Unsloth took 155 s against 71 s and peaked at 8.1 GB against 11.6 GB: no speed gain here
(xformers did not load for this torch build, so plain attention; Unsloth's gradient checkpointing; compile time weighs
on 12 steps). Under the rule above, version 4 trains with the current trainer, on the same stack as versions 1 and 3.

## 2026-11-11: test set 2 result with both judges (frozen campaign, 12 held-out companies)

Codex judged all 133 packets validly (118 before its account's usage limit, 15 after the reset at about 19:00; the
failed attempts are archived, no valid judgment was redone). Both judges scored all 144 runs.

| | base (staged prompt) | trained (version 1) | trained minus base, paired, 95% case-cluster bootstrap |
|---|---|---|---|
| Claude | 0.48 | 0.89 | +0.41 [0.24, 0.57] |
| Codex | 0.66 | 1.29 | +0.63 [0.43, 0.84] |
| **mean of judges (primary)** | **0.57** | **1.09** | **+0.52 [0.33, 0.70]**, 72 pairs, 24 cases |

Agreement: Spearman 0.95 over 144 episodes, mean absolute difference 0.30. By company (mean of judges): kingspan
+1.09, mettler +1.10, tennant +1.05, ansell +0.67, laerdal +0.64, hach +0.55, winterhalter +0.50, belimo +0.30, testo
+0.29, draeger +0.19, frankecoffee -0.05, hoshizaki -0.10: higher for 10 of 12.

## 2026-11-11: a second Codex judge on gpt-6-sol, for the exploratory version 3 comparison (Hatem: "use sol")

The frozen Codex judge (gpt-6-astra) exhausts the ChatGPT Plus allowance after about 120 judgments, so the 340 version
3 judgments would take about a day of resets. A new backend `codexsol` (judge-v1-four-backends-4): gpt-6-sol through
the same pinned CLI 0.166.0, sandbox, prompt and settings (reasoning effort medium); only the model differs. Qualified
under the same scoring rule on the same 40 packets (`reports/judge/codexsol_score_qualification.json`: sound above
flawed in 20 of 20 clusters, 0 invalid, no retry). It is a different judge from `codex`: the final test and test set 2
keep their Claude and gpt-6-astra results; codexsol scores base, version 1 and version 3 together on both version 3
packet sets, and its scores are reported beside the Claude Code judge's, never mixed with gpt-6-astra's. The 50 or so
gpt-6-astra judgments already made on the test set 2 version 3 packets are kept and not used.

## 2026-11-11: dig then reason with the status check: the app default, and its test (Hatem: "make it the default in the app. combine it with the status check and test it properly")

Fixed before any run of the combination. **The system:** one server holds versions 1 and 3; version 1 writes the
brief, frame, status, status-reading and evidence stages, version 3 every later stage (route
`default=1,brief=0,frame=0,status=0,status_reading=0,evidence=0`), with the status check on (final rule of 17:55).
- **Development first** (15 cases, 3 attempts, the two-adapter server): the combination, compared with the judged
  arms of the switching test (v1, v3, dig_then_reason without the status check). A check that the combination runs,
  not a selection: the rule and the status design are already fixed.
- **Test: test set 2** (12 companies, 24 cases, 3 attempts, 72 runs per arm). No fresh held-out companies exist and
  building a third set takes about a day, so test set 2 is used, with this stated: the routing rule was chosen on
  development only and the status check was designed on development and Aquaporin (final test), so nothing in the
  system was selected on test set 2; but test set 2 has been run before (v1, base, v3), and we know v3 scores higher
  than v1 there. Arms run now: `combined` (the system) and `dig` (the route without the status check, to separate the
  two changes). Compared with the frozen base, v1 and v3 runs of the same cases and attempts.
  Primary: combined minus v1, paired, mean of the Claude Code and gpt-6-sol judges, 95% case-cluster bootstrap, all
  five arms judged together blind. Also: combined minus v3, combined minus dig, finished runs, refusals.
- **Final test, secondary and labelled:** the same two arms on the 16 cases; Aquaporin informed the status check, so
  its numbers there are a diagnostic of the fix (reads the insolvency records, what it recommends), not a test.
- Whatever the result, version 1's frozen results stand; the paper reports this as a system built after them.

## 2026-11-11: teacher run stopped; Unsloth fair-test result

- **Teacher run with the status check stopped before it produced data** (Hatem, 19:25: "no need for the new data
  generation with the teacher. stop it and let's start finalizing stuff"). Jobs 755231 (40 GB worker, still downloading
  the model) and 755090 cancelled. No version 4 is trained for the submission; the status check is evaluated at run
  time with versions 1 and 3.
- **Unsloth, 60 steps on 240 rows, same LoRA and seed (job 755239):** median seconds per step after step 10: current
  trainer 5.87; Unsloth 4.50 with its offloading checkpointing and 4.50 with standard checkpointing (23% faster).
  Peak memory 11.6 GB against 8.1 and 8.9. Losses agree to within 0.003 at the steps compared. The 12-step test above
  was dominated by start-up. A future training run can use it; none is planned before the submission.

## 2026-11-11 (22:30): version 3 on test set 2 with the gpt-6-sol judge; combined-system runs finished, judging started

- **Version 3 on test set 2, two judges (exploratory; base, v1 and v3 judged together blind, 72 runs per arm).**
  Claude Code judge: base 0.49, v1 0.86, v3 1.22. gpt-6-sol: base 0.63, v1 1.27, v3 1.74. Mean of judges: base 0.56,
  v1 1.06, v3 1.48; v3 minus v1 +0.42 [0.24, 0.60] (71 pairs, 24 cases), v3 minus base +0.92 [0.82, 1.02], v1 minus
  base +0.49 [0.29, 0.69]. Judges: Spearman 0.93 on 215 runs, mean absolute difference 0.36. v3 is higher than v1 at
  10 of 12 companies (mettler -0.10, tennant -0.07). Reports: `reports/judge/test2_v3/report_claudecode_codexsol_*.json`.
  Sol on the final-test v3 packets stands at 94 of 135 (usage limit); it continues hourly.
- **Combined system, runs done** (jobs 755268, 755269, 755270, 755289, 755347, revision 64975a1). Finished runs, before
  any judging: test set 2 combined 37 of 72, dig 43 of 72; final test combined 27 of 48, dig 27 of 48; development
  combined 20 of 45. Every combined run called the status check (72, 48 and 45). Aquaporin (diagnostic, 12 runs per
  arm): combined finished 5, 3 "do not invest" and 2 "invest"; dig finished 8, 7 "invest" and 1 "do not invest".
- **Judging as planned:** `reports/judge/system_test2` (342 packets from 360 runs) and `reports/judge/system_final`
  (231 from 240): base, v1, v3, combined and dig together, blind, keys outside the repository until both judges end.
  Claude Code judge first, then gpt-6-sol through `experiments/codex_judge/run.py system_test2 system_final`.

## 2026-11-11 (23:15): the combined system on test set 2, both judges: the primary comparison is not met

Five arms judged together blind (342 packets from 360 runs, 72 runs per arm, 24 cases), Claude Code and gpt-6-sol,
no judgment missing. Mean of judges: base 0.56, v1 1.07, combined 1.28, dig 1.43, v3 1.48 (Claude Code: 0.48, 0.87,
1.07, 1.16, 1.21; gpt-6-sol: 0.63, 1.26, 1.49, 1.70, 1.74). Spearman between judges 0.90 on 360 runs.
- **Primary, combined minus v1: +0.22 [-0.00, 0.46]**, 72 pairs. The interval includes zero: not shown better than v1.
  By company: higher at 7 of 12 (hoshizaki +1.19, frankecoffee +0.94, belimo +0.82), lower at 5 (winterhalter -0.42,
  ansell -0.24).
- Combined minus v3: -0.20 [-0.38, -0.01]. Combined minus dig: -0.15 [-0.35, 0.06]. Dig minus v1: +0.36 [0.22, 0.51].
  Combined minus base: +0.73 [0.52, 0.93].
- Reading: on test set 2 the route adds nothing over version 3 alone (dig 1.43 against v3 1.48), unlike development,
  and the status check costs about 0.15, with fewer finished runs (37 of 72 against 43). Version 1's frozen results
  stand. The final-test packets (secondary, labelled) are still being judged.
- A full disk at 23:04 (a local container build) stopped both judges; 3 gpt-6-sol and 4 Claude Code attempts written
  empty were archived as `*_archived_disk_full` and rerun. No completed judgment was affected.

## 2026-11-11 (23:40): the public repository carries the dossier as it is

Hatem: "keep them as they are and publish them". The public build (`scripts/release/build_public_repo.py`) no longer
cuts dossier excerpts to one short quote; the public dossier is byte-identical to the private one, so public runs read
what the evaluated runs read and the frozen digests apply. Personal and internal identifiers are still replaced, and the
third-party papers stay out. The Hugging Face dataset published on 2026-11-08 still has the cut excerpts.

## 2026-11-11 (23:45): the combined system on the final test, Claude Code judge (secondary, labelled; gpt-6-sol pending)

231 packets from 240 runs, all valid. Claude Code judge, 48 runs per arm: base 0.54, v1 1.18, dig 1.13, v3 1.06,
combined 1.03. Paired, 95% case-cluster bootstrap: combined minus v1 -0.15 [-0.32, 0.01] (aqp -0.48, rational -0.23,
epro -0.06, simo +0.18); dig minus v1 -0.06 [-0.23, 0.12]; combined minus v3 -0.03 [-0.18, 0.14]; combined minus dig
-0.09 [-0.30, 0.12]; v3 minus v1 -0.12 [-0.27, 0.02]; v1 minus base +0.64 [0.49, 0.78] (the API judge gave +0.64 on
the frozen campaign). gpt-6-sol stands at 68 of 231 on the Codex usage limit and retries hourly; the two-judge numbers
replace these when it ends. Reading: no later system is distinguishable from version 1 on the final test, and on test
set 2 version 3 and dig are higher; nothing built after version 1 is shown better on both sets.

## 2026-11-12: the app default is dig then reason without the status check (Hatem: "yes")

On both test sets dig then reason scored higher without the company status check than with it (test set 2, two
judges: 1.43 against 1.28; final test, Claude Code judge: 1.13 against 1.03), and it is the best later system overall
(clearly above version 1 on development and test set 2, level on the final test). The app's default `system` model
therefore runs version 1 for the brief, frame and evidence stages and version 3 after, with the status check off;
`STATUS_CHECK=1` turns it on. Applied locally and on the hosted demo. Version 1 remains the evaluated model.

## 2026-11-12 01:10: version 4, recovery distillation for the reasoner (Hatem: "explore distilling more data ... make the model reason better"; registered before any run)

Why: version 3 reasons better than version 1 when it gets there, but it learned the second teacher's direct style
without recovery: when a call is refused it repeats it (24 of 32 final refusals on its screen were a repeated search),
and about 4 in 10 runs of every trained system stop before a recommendation. Recovery is mechanically checkable, so a
free teacher (Command A+ on the cluster; no paid API, no Claude or Codex output as data) can supply it.

1. **Harvest** (training companies only; no validation, final-test or test-set-2 company): the deployed system, dig
   then reason without the status check (version 1 for brief, frame and evidence, version 3 after), on the training
   cases, one attempt, the evaluated settings (compact prompt, 45 turns, 4 refusals in a row).
2. **States and corrections** (`aemon.teacher.corrections`, protocol correction-v1, unchanged): the states that start
   a loop (a repeat refused, a third read, a second refusal in a row) in the stages version 3 writes; Command A+
   answers each; a correction is kept only if it replays as accepted, repeats nothing and names what it acts on.
3. **Version 4**: version 3 continued on its own DeepSeek rows plus the kept corrections (corrections at most 20% of
   rows), one pass, the v3 learning rate and seed. Conversion gate v2 as for every adapter.
4. **Development screen**: dig then reason with version 3 against dig then reason with version 4 as the reasoner, the
   15 development cases, 3 attempts, one server holding both, judged together blind by the Claude Code judge.
   **Adopted as the reasoner** only if all three hold: blind quality not lower (v4 minus v3 point estimate >= 0),
   refused calls per run lower, finished runs not fewer. Otherwise version 3 stays.
5. If adopted: test set 2 and the final test, labelled exploratory (both sets have been run before), both judges
   where the Codex limit allows. Version 1 stays the frozen, headline model whatever happens.

## 2026-11-12 02:00: corrections to earlier entries, found by a number audit (the entries above are left as written)

- The 11 November status-check entry says "all 144 Aquaporin final-test runs"; it is 36 (12 base, 12 v1, 12 v3). The
  insolvency announcement did appear in search results (in all 12 base runs) but no run of the first test opened it,
  and version 3 read it in 4 of 12 runs and still recommended investing. "Never appeared in a search result" and "no
  version 3 run found" are wrong; "no v1 or base run read it" is right.
- The 11 November 00:05 entry's 288 DeepSeek investigations: 266 ran, 154 finished, 112 did not, and 22 more were
  harness errors (the 288).
- Version 2 was trained (job 752833) and stopped at its screen; the reliability report predates that round.
- Several 10 November entries are out of time order in this file; their timestamps are right.

## 2026-11-12 02:10: version 4 timing cut-off (registered before any correction exists)

The teacher step may take 10 to 25 hours on the free slices. To leave time for the screen before the deadline,
version 4 trains on the corrections kept by **13 November 14:00 CET**, whatever their number (batches unfinished then
are left out and named). If fewer than 50 are kept by then, version 4 is not trained and the plan is reported as not
completed.

## 2026-11-12 02:50: loop guards at decoding time (registered before any screen run)

**Why.** In the final-test runs of the default (dig then reason), 233 of 274 refused calls are repeats (130 repeated
searches, 103 re-assessments of a pair already assessed) and 33 are misquotes; for the combined system 213 of 322
are repeats and 94 misquotes. A run stops after 4 refusals in a row, so these loops are what "repeated errors" means.
The final-test numbers were read only to find the failure; nothing below is run on either frozen test set.

**What (development only, `--recovery`, off as evaluated; `agent/recovery.py`, `agent/loop.py`):**
- `no_repeats`: assess_evidence offers, per theory, only the sources not yet assessed for that theory.
- `quote_menu`: assess_evidence's quote is one of the sentences of the chosen source, so it cannot be misquoted.
- `resample_repeats`: a call the environment refuses as an exact repeat changed nothing, so the same state is drawn
  again (temperature 0.8, new seed), at most 3 times, before the refusal counts toward the stop. Every refused draw stays
  in the record, marked `redrawn`, and in the refused-call count.
No guard, stage rule, budget or stop is changed. A replay of the 45 development dig-then-reason runs found that
withdrawing the search tool after a repeated search would also have blocked 42 accepted calls, so that variant was
dropped before any live run.

**Screen.** Laptop GPU (the 4-bit base, the app's runtime), both arms on the same server: dig then reason as it is
against dig then reason with all three guards, the 15 development cases of the switching screen, 3 attempts, judged
together blind by the Claude Code judge (Sol as well if its limit allows). **Adopted as the app default** only if all
hold: finished runs more, refused calls per run lower, blind quality not lower (guarded minus plain point estimate >= 0).
If adopted, it is run on test set 2 labelled exploratory (that set has been run before). Version 1 stays the frozen,
headline result whatever happens.

## 2026-11-12 04:05: combined system and dig then reason on the final test, both judges

The second judge (Codex, gpt-6-sol) finished the 231 final-test packets at 04:00 (five rounds across usage limits; no
packet missing). Mean of the two judges, 48 runs per arm, case-cluster bootstrap, Spearman 0.82 between the judges:
base 0.61, version 1 1.45, dig then reason 1.44, version 3 1.35, combined 1.32.
- dig then reason minus version 1: −0.01 [−0.20, 0.18]; combined minus version 1: −0.13 [−0.32, 0.05];
  version 3 minus version 1: −0.10 [−0.27, 0.05]; dig then reason minus version 3: +0.09 [−0.10, 0.27].
- Every trained arm stays far above the base: version 1 +0.85 [0.68, 1.00] (this re-judging; the frozen result is
  +0.83 [0.69, 0.97]), dig then reason +0.84 [0.69, 0.96], combined +0.71 [0.53, 0.91].
- Per judge: Claude Code ranks version 1 first (1.18 against dig 1.13), Sol ranks dig first (1.76 against 1.72).

**Decision:** the one-judge reading of 23:45 stands with both judges: no later arm is distinguishable from version 1 on
the final test. Version 1 stays the headline model; dig then reason stays the app default as the most consistent later
system (above version 1 on test set 2 and development, level on the final test). The keys of system_test2 and
system_final (and screen3) are now published, since every judge has finished.

## 2026-11-12 05:10: loop guards, a third arm (registered after the guarded runs, before any judging result)

Mechanical result of the screen (not yet judged): plain 28 of 45 finished, 17 stopped on repeated refusals, 234
refused calls; guarded 33 of 45 finished, none stopped on refusals, 12 hit the turn limit, 139 refused calls (every
one a repeat that was redrawn). In the 12 turn-limit runs the refusal loop became an assessment loop: with repeats
masked, the model weighs every source for every theory ("neutral"), 8 of them at the test step, until 45 turns.
The budget guard of the recovery study (`budget`: exploration withdrawn when turns left <= what the step still needs
+ 3) targets exactly this (stage 1: 6 of 6 test-step dead ends rescued). **Third arm:** guarded + budget, the same
cases, seeds and server, judged blind against the other two together. The registered rule (02:50) is applied to
guarded vs plain as written; guarded + budget is judged against plain under the same three conditions, labelled as
selected after seeing the guarded runs.

## 2026-11-12 05:20: loop guards adopted (development screen, Claude Code judge, blind)

guarded minus plain: **+0.036 [−0.083, 0.151]**, 45 pairs, 15 cases (plain 1.129, guarded 1.166); higher at 5 of 6
companies (ACR +0.23, Tanita +0.23, Jotun +0.23, Neumann +0.17, Deere +0.07), lower at Hellberg (−0.27). Finished 33
against 28; refused calls per run 3.1 against 5.2; finished runs with no invented number 20 of 33 against 13 of 28.
All three registered conditions hold, so **the loop guards are adopted**: on for the app's default system (LOOP_GUARDS=0
turns them off), and run on test set 2 as registered, labelled exploratory, plain and guarded on the same laptop server
with the same seeds, judged blind together. The runner now accepts exactly these three features on test set 2 and
still refuses every experimental feature on the final test. Version 1 stays the headline result.

## 2026-11-12 06:40: guards + budget, development, both judges: adopted

The third arm (registered 05:10) finished **45 of 45** runs (plain 28, guarded 33), refused calls per run 3.1 (plain
5.2), finished runs with no invented number 26 (plain 13), experiment check passed 17 (plain 12). Judged blind by both
judges: 23 of its 45 packets are byte-identical to packets already judged (the budget guard never acted in those runs),
so they keep those judgments and the 22 new packets were judged by both judges (none missing); the three arms are
reported from the merged key and predictions.
- guards + budget minus plain: **+0.194 [0.097, 0.302]** (Claude Code +0.135 [0.056, 0.219], Sol +0.252
  [0.131, 0.393]); higher or level at all six companies (Hellberg +0.01).
- guards + budget minus guards: +0.102 [0.031, 0.178]. Plain 1.42, guards 1.52, guards + budget 1.62 (mean of judges).
- The two-judge result for guarded vs plain: +0.092 [−0.052, 0.238] (Sol +0.148, Claude Code +0.036).
All three conditions hold against plain, so **guards + budget is adopted**: it becomes the app default (LOOP_GUARDS=0
turns all four off) and runs on test set 2 as a third arm, labelled exploratory and as selected after seeing the
guarded runs. The 9 November study found the budget guard alone did not raise quality on version 1 (+0.006); with the
loop guards and the v3 reasoner it does here, on development. Version 1 stays the headline result.

## 2026-11-12 07:10: loop guards on test set 2 moved to the cluster

At 06:50 the laptop ran out of memory and its model server was stopped mid-run: the plain test set 2 arm had 26 of
72 runs, 46 failed in the harness (kept as `experiments/loop_guards/test2/laptop_aborted_*`, not used). The test set 2
run moved to the cluster, the evaluated bf16 runtime: the plain arm is the existing dig-then-reason run of test set 2
(`system_test2_dig`, the same route, settings and seeds, already judged by both judges), and the two guard arms are
jobs 756273 (guards) and 756274 (guards + budget), code 731c3c5. One version 4 teacher worker (756018) was cancelled
to free the slot; its unfinished batch is requeued by the driver. Packets identical to ones already judged keep their
judgments; the rest are judged by both judges. The rules of 02:50 and 06:40 apply unchanged.

## 2026-11-12 10:35: loop guards on test set 2, both judges (exploratory)

Jobs 756273 and 756274 finished (cluster, bf16, 24 cases × 3 attempts). Of the 144 packets, 71 were byte-identical to
packets of system_test2 already judged and keep those judgments; the 73 new ones were judged blind by both judges,
none missing. The pipeline's Sol retry check miscounted (a `grep -c || echo 0` printed two zeros) and started an
unneeded hour-long wait after Sol had judged all 73, so it was stopped and the reports were written by hand with the
same commands (`experiments/loop_guards/test2/report_both_*.json`).
- Finished: plain 43, guards 62, guards + budget 63 of 72. Refused calls per run 6.1, 3.5, 3.5. Finished with no
  invented number 34, 53, 50. Experiment check passed 14, 29, 26.
- Mean of judges: plain 1.427, guards 1.584, guards + budget 1.589.
- guards + budget minus plain: **+0.162 [0.049, 0.272]** (Claude Code +0.124 [0.023, 0.223], Sol +0.200
  [0.069, 0.329]). guards minus plain: +0.157 [0.045, 0.266] (Claude Code +0.119, Sol +0.194). guards + budget minus
  guards: +0.006 [−0.010, 0.022].
- Lower at Testo for both judges (−0.317, mean of judges), level at Kingspan; judge agreement Spearman 0.65.
Reading: the development result holds on test set 2 for the guards; the budget guard's development gain does not
reappear (few guarded runs reach the turn limit here). Exploratory, since the set had been run before and the guards
were built after every frozen result. Version 1 stays the headline result; the app default is unchanged (guards + budget).

## 2026-11-12 11:35: quote-menu bug fixed; guards + budget rerun on test set 2 (registered before the run)

Reading the unfinished guarded runs of test set 2: all 6 Belimo runs of each guarded arm stopped at the assessment
stage on four `arguments` refusals in a row ("quote at least 3 words and 15 characters"). The quote menu offered every
excerpt sentence of 12 to 420 characters, so a dateline ('DANBURY, Conn.', 2 words, 14 characters) was on the menu,
the model picked it, and the environment refused it each time. This is a bug in the guard, not a model failure: the
menu was meant to hold only quotes the environment accepts. No development run was affected (0 such refusals in the
90 guarded development runs); on test set 2, 24 refusals in 6 runs per arm, every one of those runs stopped by it.

**Fix** (`agent/recovery.sentences`): the menu holds only sentences the environment accepts (at least 3 words and
MIN_QUOTE characters once normalised, at most 420). Nothing else changes.

**Run.** The guards + budget arm (the app default) again on test set 2 with the fix, same route, settings, seeds,
cases and attempts (cluster, bf16); runs whose menus did not change are expected to reproduce byte for byte and keep
their judgments; the rest are judged blind by both judges together with the existing plain arm. Reported as a corrected
rerun next to the 10:35 result, which stays in the record unchanged; labelled exploratory (test set 2 has now been used
to find this bug). Nothing is adopted or dropped on this result: the guards stay the app default either way.
A second pattern, not fixed: 2 Testo runs per arm loop between a repeated search (redrawn) and an accepted re-read of
a source until the turn limit; a reread mask was tested on 9 November and did not raise quality, so it is left alone.

## 2026-11-12 13:18: corrected guards + budget rerun on test set 2, result (exploratory)

Job 756932 (code 4573c82), as registered at 11:35. 66 of 72 runs reproduced the earlier guards + budget arm call for
call and kept their judgments; the 6 that changed are exactly the Belimo runs, all of which stopped on the dateline
before and all of which finish now. The 6 new packets were judged blind by both judges (140 packets, none missing).

| Arm (72 runs) | Finished | Refused/run | No invented number | Experiment check | Mean of judges | Claude Code | gpt-6-sol |
|---|---|---|---|---|---|---|---|
| As evaluated | 43 | 6.1 | 34 | 14 | 1.427 | 1.158 | 1.696 |
| Guards + budget (10:35) | 63 | 3.5 | 50 | 26 | 1.589 | 1.282 | 1.896 |
| Guards + budget, quote fix | 69 | 3.2 | 55 | 28 | 1.638 | 1.322 | 1.954 |

- Fixed minus as evaluated: +0.211 [0.088, 0.334] (Claude Code +0.164 [0.054, 0.279], gpt-6-sol +0.259 [0.115, 0.402]).
- Fixed minus before the fix: +0.049 [0.000, 0.129]; by company, Belimo +0.59 and every other company 0.
- Judge agreement over the 216 runs: Spearman 0.588, mean absolute difference 0.594.
- Reported next to the 10:35 result, which stays unchanged. Exploratory. Nothing adopted or dropped: the guards (with
  the fixed quote menu) were already the app default. Files: experiments/loop_guards/test2_fix/.

## 2026-11-12 14:45: version 4, gate and screen automated (no change to the 01:10 and 02:10 plan)

`experiments/v4_recovery/after_rows.sh` runs steps 3 and 4 once the driver has built the corrections: at least 50
kept (02:10), then `jobs/train_v4.sbatch`, then, once training completes, `jobs/v4_screen.sbatch`: conversion gate v2
on the version 4 adapter (prompts from version 3's DeepSeek validation rows), and only if it passes, one server holding
versions 1, 3 and 4, dig then reason with version 3 and with version 4 as the reasoner, the 15 development cases,
3 attempts, judged together blind by the Claude Code judge, with the 01:10 adoption rule applied as written. Neither
arm uses the loop guards: they were adopted after this plan, and they would mask the recovery version 4 is meant to
learn. The guarded system stays the app default whatever the screen shows.

## 2026-11-12 16:10: version 4 cut-off moved to 12 November 21:00 (Hatem; replaces the 02:10 cut-off time)

Hatem: "it's too much time. it doesn't have to finish. can we use the data that we will generate today only?" The
cluster quota filled at 14:25 and stopped four teacher workers (two batches lost), so the full queue would end on the
morning of 13 November. The teacher step now ends at **12 November 21:00 CET** (`experiments/v4_recovery/cutoff.sh`):
the batches finished by then are merged, the rest are left out and named, and the teacher jobs are cancelled. The
50-correction minimum of 02:10 stands. At 16:00, 7 of 23 batches were answered (140 states) and 30 corrections kept
(theories 19, test 9, challenge 1, position 1); at about 4 kept per batch and two workers, about 55 are expected.
Everything after (training, gate v2, screen, adoption rule) is unchanged. With about 55 corrections next to 3,611
DeepSeek rows (1.5% of rows), a small effect is the expected outcome, and that is how it will be reported.

## 2026-11-12 16:30: version 4 stopped; loop guards on the final test (registered before the run)

**Version 4 stopped** (Hatem, 16:25: "ok forget about v4, run the loop guard test"). The loop guards already address
the failure version 4 targeted (repeats after a refusal) without training, and about 55 corrections (1.5% of rows)
could not move a 45-run screen detectably. Teacher jobs 757709 and 757766 cancelled; the 7 answered batches (140
states, 30 kept corrections) stay under experiments/v4_recovery as a stopped step. No version 4 is trained.

**Loop guards on the final test (exploratory: the final test has been run before and its frozen result stands).**
- One arm: dig then reason with the guards and the budget guard, the app default
  (`RECOVERY=no_repeats,quote_menu,resample_repeats,budget`, quote menu as fixed at 11:35), the 16 final-test cases,
  3 attempts, the same route, prompt and settings as the final-test dig-then-reason arm (`system_final_dig`, 48 runs).
- Judged blind by both judges together with that arm; packets identical to already-judged ones keep their judgments.
- Reported: guards + budget minus dig then reason as evaluated, per judge and mean of judges, by company, with
  finished runs, refused calls, and the no-invented-number and experiment checks, whatever the result. Nothing is
  adopted or dropped on it, and version 1 stays the headline model.
- 16:20: the first submission (job 757853) was refused by the runner's split check, which allowed the adopted guards on test set 2 only; the check now allows the same four on the final test, nothing else; resubmitted.

## 2026-11-12 17:55: loop guards on the final test, result (exploratory)

Job 757893 (code 61ae91c), as registered at 16:30. 96 packets (48 new, 48 reused from system_final), none missing.

| Arm (48 runs) | Finished | Refused/run | No invented number | Experiment check | Mean of judges | Claude Code | gpt-6-sol |
|---|---|---|---|---|---|---|---|
| Dig then reason, as evaluated | 27 | 5.7 | 25 | 9 | 1.441 | 1.126 | 1.756 |
| Guards + budget | 45 | 2.9 | 37 | 11 | 1.560 | 1.208 | 1.912 |

- Guards + budget minus as evaluated: +0.119 [−0.000, 0.249] (16 cases); Claude Code +0.081 [−0.011, 0.185],
  gpt-6-sol +0.156 [0.007, 0.334]. By company: simo +0.388, aqp +0.036, rational +0.036, epro +0.014.
- Judge agreement: Spearman 0.421 over 96 runs, mean absolute difference 0.667.
- Read as registered: more runs finish and fewer calls are refused, as on the other two sets; the quality gain is not
  clearly above zero here and rests mostly on one company. Nothing adopted or dropped; version 1 stays the headline.

## 2026-11-12 18:15: grounded beliefs, development screen (registered before any run)

**Why.** On the final-test runs of the app default (dig then reason with the loop guards), the judges' lowest scores
are evidence judgement (Claude Code 0.46, gpt-6-sol 0.96) and the recommendation (1.00 and 1.16): every Claude Code
recommendation score is 1 of 3. Their reasons repeat one pattern: the favoured theory is rated 'likely' with no
supporting weighing, contradicting evidence the run itself weighed (a going-concern warning) is not addressed, and the
recommendation commits before its own test. The 10 November attempt (V1.1, `agent/experimental/grounded.py`) narrowed
the favoured theory and failed on the challenge rule; this one leaves the favoured theory and all text free.

**What (`--recovery grounded_beliefs`, development only; `agent/recovery.py`, `agent/tool_schemas.py`, `agent/loop.py`):**
state_position and finish offer 'likely' or 'very likely' only for a theory with at least one supporting weighing of a
real (not simulated) source, and take the beliefs before the favoured theory and the recommendation text; at the
position, update and conclude steps the state shows a ledger of the run's own weighings per theory.

**Screen.** Development, the 15 cases × 3 attempts, cluster bf16, dig then reason route. Two arms run side by side:
A, the app default (`no_repeats,quote_menu,resample_repeats,budget`), and B, the same plus `grounded_beliefs`. Judged
blind by both judges; packets identical to ones already judged keep their judgments.
**B is taken forward** (test set 2 and the final test, exploratory) only if all hold: mean-of-judges B minus A above 0;
the recommendation dimension higher for both judges; finished runs at most 2 fewer than A. Otherwise it is reported as
tried, and the app default stays A.

## 2026-11-12 19:55: evidence first, development screen (registered before any run)

**Why.** Evidence judgement is the lowest judged dimension on the app default's final-test runs (Claude Code 0.46,
gpt-6-sol 0.96). The judges' reasons: a quote counted as support for a theory it does not address, and the kind of
evidence mislabelled (a company's estimate called an independent study).

**What (`--recovery evidence_first`, development only, with quote_menu):** assess_evidence takes the quote and what it
does not show before the evidence kind and the direction; for a source the environment marks as a company claim (shown
to the model as its class when read), the only kind offered is company_assertion (the dossier annotates 622 of its
647 company claims so). The experiment check was also looked at and is left alone: most of its failures follow a
per-case `test_warranted` label that FINAL_TEST_DIAGNOSIS found contestable, and steering towards it would be tuning
to the label.

**Screen.** Same cases, attempts, route and settings as the 18:15 screen, two more arms run side by side now (so they
do not wait for the 18:15 judging): C = A + `evidence_first`, D = B + `evidence_first`. Judged blind by both judges.
Rule, registered: C is taken forward if mean-of-judges C minus A is above 0, evidence judgement higher for both judges,
and finished runs at most 2 fewer than A; D is compared with B in the same way. If both B and D pass, the arm with the
higher mean of judges is the one taken to test set 2 and the final test.

## 2026-11-12 21:35: grounded beliefs, development screen result: not taken forward

Jobs 758126 (A) and 758127 (B), code 33eaed0; 90 packets, all new (A did not reproduce the earlier development runs
call for call, the code having changed since), judged blind by both judges, none missing.

| Arm (45 runs) | Finished | Refused calls | Strong belief in the finish | Mean of judges | Claude Code | gpt-6-sol |
|---|---|---|---|---|---|---|
| A, app default | 43 | 150 | 40 of 43 | 1.565 | 1.290 | 1.840 |
| B, + grounded beliefs | 44 | 149 | 33 of 44 | 1.554 | 1.288 | 1.820 |

- B minus A: −0.011 [−0.046, 0.026] (Claude Code −0.002 [−0.045, 0.041], gpt-6-sol −0.019 [−0.073, 0.033]).
- The recommendation dimension is barely higher for both judges (Claude Code 1.05 to 1.07, gpt-6-sol 1.07 to 1.11), and
  finished runs are not fewer, but the mean of judges is not above 0, so the registered rule is not met. B changed the
  conclusions as designed (fewer unearned strong beliefs; 10 recommendations to test first, none in A), and the judges
  did not score them higher. Reported as tried; the app default stays A. Judge agreement: Spearman 0.455.
- Judging note: gpt-6-sol's first rounds hit its usage limit, and the retry did not clear failed results; the retry
  now moves them aside (as `experiments/codex_judge/run.py` does). No judgment was changed.

## 2026-11-12 21:55: evidence first, development screen result: taken forward (D) to test set 2 and the final test

Jobs 758434 (C) and 758435 (D), code 2ff6c41; judged blind by both judges with A and B (180 packets, 90 new, none
missing).

| Arm (45 runs) | Finished | No invented number | Mean of judges | Claude Code | gpt-6-sol | Evidence judgement (CC / Sol) |
|---|---|---|---|---|---|---|
| A, app default | 43 | 30 | 1.565 | 1.290 | 1.840 | 0.62 / 1.07 |
| B, + grounded beliefs | 44 | 28 | 1.554 | 1.288 | 1.820 | 0.60 / 1.11 |
| C, A + evidence first | 43 | 24 | 1.625 | 1.349 | 1.901 | 0.96 / 1.20 |
| D, B + evidence first | 43 | 23 | 1.631 | 1.342 | 1.920 | 0.91 / 1.20 |

- C minus A: +0.060 [0.029, 0.091] (Claude Code +0.059 [0.020, 0.098], gpt-6-sol +0.061 [0.016, 0.109]); higher at
  all 6 companies. D minus B: +0.077 [0.034, 0.122]; D minus A: +0.066 [0.028, 0.107]. Judge agreement over 180 runs:
  Spearman 0.323.
- Both pass the registered rule. The 19:55 entry says "if both B and D pass"; it was meant to read "C and D" (B is the
  18:15 arm, already decided). Read as meant, the arm with the higher mean of judges is taken forward: **D**
  (1.631 against 1.625; the gap is well inside the noise).
- A regression to watch: the no-invented-number check passes in fewer finished runs (A 30, C 24, D 23).
- **Next (registered now):** D on test set 2 (24 cases × 3) and on the final test (16 cases × 3), cluster bf16, the same
  route and settings, labelled exploratory, each judged blind by both judges together with that set's app-default run
  already judged (test set 2: `loop_guards/test2_fix/guarded_budget_fix`; final test: `loop_guards/final/guarded_budget`).
  Reported: D minus the app default per set, mean of judges and per judge, evidence judgement, finished runs and the
  checks, whatever the result. The runner's split check now also allows these two features on those sets.

## 2026-11-13 00:10: evidence first, final test result; app default rule fixed before test set 2's second judge

**Final test** (job 759075, code c47cd8e; 96 packets, 48 reused, none missing): D minus the app default **+0.061
[0.004, 0.113]** (Claude Code +0.095 [0.021, 0.169], gpt-6-sol +0.028 [−0.047, 0.095]); higher at all 4 companies;
evidence judgement 0.46 → 0.98 (Claude Code) and 0.96 → 1.31 (gpt-6-sol); finished 45 → 46; experiment check 11 → 16;
no-invented-number check 37 → 30 passed. Judge agreement: Spearman 0.142.

**The numbers check, read.** Splitting each failure by where its numbers come from: runs with a number found nowhere,
not even in the run's own test design, are development 9 → 8 (A → D), final test 3 → 2, test set 2 7 → 7. The extra
failures are recommendations that restate the run's own test thresholds ("run X; if purchase intent reaches 35%…"),
which the check counts as claims because they sit in the recommendation field. The check is unchanged and its counts
are reported as computed, next to this split.

**App default rule**, fixed now, before gpt-6-sol has judged test set 2 (only the Claude Code judge has: +0.023
[−0.013, 0.059], with D finishing 65 of 72 against 69): D becomes the app default if the mean-of-judges difference on
test set 2 is at least 0, as on development and the final test. Otherwise the default stays the loop guards alone.
Either way all three sets are reported, with finished runs and both checks.

## 2026-11-13 01:00: Nour's HPC calibration: same behaviour from the official base GGUF

The second cluster account holds the official `CohereLabs/tiny-aya-global-GGUF` bf16 file (sha256 fe68bac5…), not
our own conversion (4d884566…). To learn whether runs on the two accounts can be compared, arm A of the
grounded-beliefs screen (15 development cases × 3, loop guards, code af89d21) was rerun there (job 759286) and compared
run by run with the original (`experiments/grounded/A.json`).

All 45 runs are identical in every field the evaluation reads: calls, searches, sources read, theories,
assessments, position, tests, final answer and stop reason (43 finished, 2 stopped on repeated errors, 6 end-to-end
successes, 150 refused calls, 40.9 calls per run on both). Only timing and per-turn completion-token counts differ
(168,378 against 170,049 tokens; 1,664 of 1,697 turns), so the two files encode the same weights and differ in how
tokens are counted. Runs from the two accounts can be treated as the same model. Nothing else changes: no
comparison already reported mixes accounts.

## 2026-11-13 02:40: evidence first, test set 2 result; the app default changes

**Test set 2** (job 759074, code c47cd8e; 125 packets, 62 new, judged blind by both judges, none missing; gpt-6-sol's
first five rounds hit its usage limit and judged nothing, the sixth judged all): D minus the app default **+0.029
[−0.003, 0.061]** (Claude Code +0.023 [−0.013, 0.059], gpt-6-sol +0.035 [−0.015, 0.085]); higher at 9 of 12
companies (Belimo −0.005, Mettler −0.031, Kingspan −0.036); judge agreement Spearman 0.335. Evidence judgement
0.56 → 0.82 (Claude Code), 1.06 → 1.21 (gpt-6-sol); recommendation 1.03 → 1.12 and 1.16 → 1.18.

**Finished runs 69 → 65.** Five runs that finished under the app default stop under D: Draeger and Belimo repeat a
finish whose would_change_if exceeds 300 characters, Kingspan (attempt 2) ends on finishes cut off by the per-turn
token limit, Kingspan (attempt 1) states a position without challenging its favoured theory, Winterhalter reaches the
turn limit. One run that stopped (Tennant, repeated errors) finishes. The same refusals occur under the app default
(would_change_if 4 times there, 7 here); none is a bug in the new features. A schema length limit on would_change_if
would remove the first kind; not built.

**Numbers check.** Fails in 32 finished runs against 14; runs with a number found nowhere, 7 → 7.

**Rule (00:10):** the mean-of-judges difference is at least 0, so **D becomes the app default** (`app/server.py`:
`LOOP_GUARDS` adds `grounded_beliefs` and `evidence_first`). Across the three sets: development +0.066 [0.028, 0.107],
test set 2 +0.029 [−0.003, 0.061], final test +0.061 [0.004, 0.113]; all exploratory. Table:
`scripts/release/evidence_first_table.py`.

## 2026-11-13 morning: an outside review of the write-up, and what changed

A review of the README (pasted by Hatem) made six points. Each was checked against the saved reports; all held.
Nothing was rerun or rejudged, and the registered numbers are unchanged.
- **Procedure, not judgement.** Confirmed: both judges gave 1 of 3 to every finished recommendation on the final test
  (28 fine-tuned, and the base model's 4). The Simonelli run shown as an example counts a quote about cafés as support
  for a home machine, from a blog post labelled an independent study; its replay page and the README now say so.
- **Intervals.** The 16 final-test cases are 4 companies × 4 variants. Resampling companies
  (`scripts/release/robustness.py`, `reports/judge/robustness.json`): final test +0.83 [0.63, 1.05] bootstrap, [0.44,
  1.23] cluster-robust t (3 df); test set 2 +0.52 [0.29, 0.75], [0.25, 0.78]. The case-cluster interval stays the
  registered one; the company-level ones are reported beside it.
- **Baseline.** 25 of 48 base runs stop at the context limit, and an unreached stage scores 0. Comparing each pair only
  on dimensions both runs were scored on: +0.92 [0.83, 1.01] (final test), +0.90 [0.81, 0.99] (test set 2).
- **Absolute scores.** The judges agree on order, not level (framing 1.62 against 2.90). No human scores exist; Hatem
  asked for Codex scoring instead, which would add a third model's view, not a human anchor, so none was run and the
  limit is stated.
- **Scope.** One question template; stated as a limit.
- **Length.** Everything after the second test moved to `docs/FINAL_SYSTEM.md` (README 59 KB → 44 KB), with a summary
  table in its place; the teacher audit (74% of its recommendations use a number from no source) moved next to the
  result.
- **Presentation, after a second review** (Hatem: "this is a hackathon not a scientific research"): the README now
  leads with what the agent is for (an auditable first pass, run locally), and with efficiency (61 calls per finished
  investigation against 242; refused calls 14% of calls against 29%; 8% with the loop guards). Detailed intervals for
  the later systems, per-company losses and the Simonelli critique live in `docs/FINAL_SYSTEM.md`, the paper and this log
  rather than in the README's summary. No number was changed or removed from the repository.

## 2026-11-13 afternoon: the final system as a result

Hatem asked for the work after the frozen tests to be presented as the final result rather than as exploratory.
`docs/LATER_WORK.md` is renamed `docs/FINAL_SYSTEM.md` (links in this log updated), and the README leads with the
final system: dig then reason with the loop guards and evidence first, which the app runs. A third review then
asked to keep the disclosure, and it is kept everywhere the final system is reported:
- the final system was built after both frozen tests had been run and read; the loop guards came from the refused calls
  of the final-test runs, evidence first from the judges' lowest dimension there, and a quote-picker bug was found on
  test set 2;
- it is measured on the same cases, so **version 1's +0.83 [0.69, 0.97] and +0.52 [0.33, 0.70] stay the run-once
  result**; the README's tiles are labelled by system.

**New number, from saved judgments only** (`scripts/release/final_system_vs_base.py`,
`reports/judge/final_system_vs_base.json`): the final system (arm D of `experiments/grounded/`) against the base model,
paired by case and attempt, both judged by Claude Code and Codex on `gpt-6-sol` with the same instrument (cca85a72…)
in separate batches. First test's cases: 1.62 against 0.61, **+1.02 [0.92, 1.10]** (companies resampled [0.93,
1.12]; Claude Code +0.76, gpt-6-sol +1.27; 4 of 4 companies higher). Second test's cases: 1.67 against 0.56, **+1.11
[1.01, 1.20]** (12 of 12). Finished runs: 46 of 48 and 65 of 72 (base 4 and 2); 39 calls per finished investigation on
the first test (base 242); 7.5% of calls refused (base 28.8%).

**Showcase run.** The 60-second view now opens a final-system run (RATIONAL, `rational-new-evidence-irrelevant`,
attempt 2: fifteen sources weighed, each with what its quote does not show; recommends a test before committing;
mean of judges 1.83). The three version 1 showcase runs weigh two sources each, and two of them mislabel a company's
claim or a blog post as an independent study.

## 2026-11-13: a closed-model baseline, Claude Haiku 5.5 (registered before any run)

Hatem asked for a Haiku baseline; two outside reviews had asked for one. Claude Haiku 5.5 (`claude-haiku-5-5`) is the
cheapest current closed model and the one our cost table says would undercut self-hosting, so its quality is the
missing comparison. It is a baseline only: **its outputs are never training data** (provider terms; the provenance
manifest marks every Claude episode as a control).

**Setup, fixed before the run.** Both test sets, every case, 3 attempts (48 and 72 runs). The base model's
best-prompt setup: prompt `staged` (the full transcript; Haiku's context is 1M, so it never reaches the context limit
the base model hits), the same environment, tools, stage controller and limits (45 turns, 4 refusals in a row).
Anthropic API, `--backend claude --claude-model claude-haiku-5-5`, effort `medium` (the model's default), adaptive
thinking (the model's default), no seed or temperature, so runs do not repeat exactly. One development case first as
a smoke test, which selects nothing. Spending cap: $10 for the whole baseline, on the Claude ledger.

**Judging.** Blind, by the same two judges and instrument as every other comparison (Claude Code and Codex on
`gpt-6-sol`), with the base model, version 1 and the final system in the same packet set; judgments of packets already
judged are reused. A Claude judge scoring a Claude model may favour it; both judges are reported separately.

**Reported whatever it shows:** the final system minus Haiku, version 1 minus Haiku, and Haiku minus the base model
(mean of judges, case-cluster bootstrap), finished runs, calls per finished investigation, refused calls, and cost per
investigation. No decision about the final system depends on it.

### Result (14:20): Claude Haiku 5.5 does better than the final system, for less

Runs: `experiments/haiku/` (`run.sh`; the merged reports `final_merged.json` and `test2_merged.json`). Anthropic
returned HTTP 500 after the SDK's retries on 29 of the 120 episodes (10 and 19); each was rerun until it completed
(`rerun.sh`; three needed a second or third try), which is the API's fault, not the model's. A reply cut off at the
output limit while thinking left an empty text block that the API refuses in the history; the backend now drops it
(found on the development smoke run, fixed before the test runs). Total Haiku spend $1.06 (ledger total $47.37 of the
$60 cap).

Judging (`judge.sh`, `finish.sh`): base, version 1 and the final system reused their judgments; the 120 Haiku packets
were judged by both judges. The Claude Code judge's answer for 5 Haiku runs (3 and 2) kept failing the instrument's
validity check (a critical red flag on a run the environment accepted), so those runs have no mean of judges and are
left out of the pairs. The 15-minute pause between judging rounds, inherited from the cluster scripts, was dropped:
these failures are not rate limits.

| | Base | Version 1 | Final system | Haiku 5.5 | Final system minus Haiku | Haiku minus base |
|---|---|---|---|---|---|---|
| Final test, mean of judges | 0.61 | 1.45 | 1.62 | 2.28 | −0.67 [−0.79, −0.52] (45 pairs) | +1.68 [1.51, 1.84] |
| Test set 2, mean of judges | 0.56 | 1.07 | 1.67 | 2.30 | −0.63 [−0.75, −0.52] (70 pairs) | +1.75 [1.65, 1.85] |

- Per judge, final system minus Haiku: Claude Code −0.90 and −0.86, Codex −0.43 and −0.42. Lower at every company (4 of
  4, 12 of 12) and on all nine dimensions; largest on the recommendation (1.06 against 1.95, final test) and the causal
  mechanism (1.97 against 2.83).
- Haiku runs: finished 44 of 48 and 63 of 72; 22.2 and 20.8 calls per run; 24 per finished investigation; 13.9% and
  12.1% of calls refused; $0.0085 and $0.0083 per investigation; 71 and 77 seconds.
- **Consequence for the write-up.** The claim that self-hosting is cheaper than a closed model held against Opus, not
  against Haiku, which costs a quarter as much per investigation and scores higher. The README, model card and paper
  now say so; the case for aemon is a small open model that runs offline with the case data kept local, and the
  measured gain of fine-tuning over its own base model.

## 2026-11-13 afternoon and evening: the demo, the sign-in, the names, and two outside reviews

- **Demo.** Modal's spend limit had taken the live demo down. Hatem took Hugging Face PRO (free Docker Spaces now need
  it), and the demo is the Space `HatemSaadallah/aemon` (`scripts/release/build_space.py`; CPU, the final system, four
  seeded investigations). Runs made on the Space do not survive a restart; accepted for a demo.
- **Sign-in by username alone** (Hatem's request): a new name opens an account in every company, seeded with the
  finished investigations; the same name reopens it; no password, so a name is not private; new accounts limited per
  hour. The Space page shows the app in a frame from another site, where a strict cookie is never sent, so the hosted
  copy sets a partitioned, secure, SameSite=None session cookie (`CROSS_SITE_COOKIE=1`); locally the strict cookie stays.
- **Names.** The model (`tiny-aya-global-strategy-agent`) and the dataset (`strategy-agent-investigations`) were
  renamed `HatemSaadallah/aemon`; the old ids redirect, the collection followed, every reference updated. The version 3
  adapter was also placed at the top level of the model repository (`v3_adapter.gguf`; the `exploratory/` copy stays).
- **Article.** Hatem reversed the 12 November decision and posted a Hugging Face article
  (https://huggingface.co/blog/HatemSaadallah/aemon), first as the README verbatim; a 500-word abstract was written
  (`docs/ABSTRACT.md`).
- **Two outside reviews of the write-up** (pasted by Hatem; the reviewer worked from a ZIP snapshot older than the
  Haiku result). Checked against the current files: (1) *dataset packaging*, confirmed and fixed: `training/rows.jsonl`
  held all 4,302 version 1 rows and the Hub config exposed it as `train`, so the 411 rows on the 6 validation companies
  were loaded as training data; the release now publishes `rows.jsonl` (3,891, training companies) and
  `validation_rows.jsonl` (411) as `train` and `validation`, with a loading section in the card (dataset commit
  aef81d73); (2) *which aemon is which*, confirmed: a table near the top of the README and the model card now maps
  version 1, the final system and the experimental variants to their files and numbers; (3) *the closed-model
  comparison* was already honest after the Haiku result; the licence (CC-BY-NC 4.0) now sits next to the first "open"
  in the README, model card and abstract; (4) *demo before chronology*: the app section moved to the top matter;
  (5) *labels*: done since the snapshot; the efficiency metric now says refused calls are included; (6) *one job per
  page*: the article is rewritten as a story within Lexsi's nine sections (kickoff slide 29; the website's rules add
  the metrics and why, the rationale for data and models, before-and-after on more than one metric, and an ROI
  comparison), with a "why these metrics" paragraph before the results in both the README and the article.
  The website now gives the deadline as 15 November 2026, 11:59 PM AoE.

## 2026-11-15: the article checked against Lexsi's write-up checklist

Lexsi published a write-up checklist (required, optional and track-dependent items). The article kept its nine sections
and gained the required front matter (one-line claim; tracks and problem statements as a numbered list, 3 and 7, with 2
measured; an abstract under 500 words, 495; headline before → after; base model and method in one line; a "for judges:
one minute" box), a why-this-problem paragraph, the Track 3 dataset items (languages, English only; the leak check,
splits by company with no embedding or MinHash check and why; the tool environment and trajectories; no retention
benchmark, declared), an explicit metric list with directions and the judge check, a training-setup table (version 1:
LoRA 16/32/0.05 on all linear layers, 1e-4, cosine, effective batch 4, 2 epochs, 1,971 steps; version 3: 2.5e-5, one
epoch, 10% warm-up), compute used and cost per 1,000 investigations ($32 self-hosted, $8.40 Haiku measured, $250 Opus
measured), an expected before → after table in section 8 labelled as a forecast, and in section 9 reproduction
(requirements, layout, commands), a declaration that no work predates the hackathon (first commit 1 November 2026), an
LLM usage statement, references and an appendix of prompt and rubric links. Not added, pending the authors: author
contributions and an approximate share for the LLM usage statement.

## 2026-11-15: five reviewer notes on the README and article, and a retention check

An outside reviewer's notes, checked against the files and acted on: (1) a **threat model** (what the environment
defends against: fabricated quotes, simulated results as evidence, post-dated sources, company claims as evidence,
invented numbers; and what it does not: a poisoned dossier, an adversarial user, prompt injection in a source, judges
that fluent prose can game) added to section 4 of the README and the article; (2) a **general-capability retention
check**, registered here before it ran: base Tiny Aya (the evaluated bf16 GGUF) against the same llama-server process
with the version 1 adapter at scale 1 and with the version 3 adapter at scale 1, on 500 MMLU test items (every subject,
evenly) and 300 ARC-Challenge test items, zero-shot, scored by the most probable letter among the first token's top-20
log-probabilities (`scripts/bench/`, `jobs/retention.sbatch`; items sha256 7ce21200…); the result is reported whichever
way it goes, with a 95% bootstrap interval over items on the paired difference; a first run that parsed a generated
reply instead (job 766356) is discarded because the base model answered 411 of 800 items without a letter, a format
failure rather than a capability one, which the log-probability scoring removes; (3) the **Track 3 metrics by name**
(task success, tool-call accuracy, latency) per company and per test, from the saved runs
(`scripts/release/track3_metrics.py`, `reports/track3_metrics.json`), in both documents; (4) the README's opening and
tiles now carry the **company-level interval** (0.44 to 1.23, company-cluster t) beside +0.83 and label the final
system's numbers "not held out" wherever they appear; (5) the **README cut** from 7,276 to about 6,900 words (the early
development, failure diagnosis, teacher audit, parts table and lessons condensed with links; the beliefs direction
check moved to `docs/FINAL_TEST_DIAGNOSIS.md`), and the **retired first conversion gate** explained in one sentence in
the controls section with a note beside `reports/judge/final/final_test_trained_conversion.json`, whose `passed:
false` is that retired criterion. The reviewer's follow-up: the judge-qualification account is now the same in both
documents (frozen tests: Claude and Codex 20 of 20 each, Claude after requalification; final system: Claude Code 19
of 20, Codex on gpt-6-sol 20 of 20), the Haiku cost is $0.008 everywhere, and both documents explain why the second
test's gain is smaller (version 1 finished fewer runs there; on the stages both runs reached the tests agree, +0.92
and +0.90).

**Retention result (job 766367, 15:19).** Base 60.9% (MMLU 53.4%, ARC-Challenge 73.3%); version 1 adapter 60.9% (53.2%,
73.7%); version 3 adapter 60.9% (53.0%, 74.0%). Paired differences 0.0 points, 95% bootstrap [−1.3, +1.3] and
[−1.4, +1.4]; the adapters change the answer on 42 and 52 of 800 items and the changes cancel. Files:
`reports/retention/` (results, replies, items, hashes: base GGUF 4d884566, v1 41794b57, v3 ea919380). Reported in the
README, the article and the model card.

## 2026-11-18: first decision-model measurement, registered before it runs

Product plan workstream A, the zero-training step. Two typed sub-decisions with gold labels already in the repository,
built from the saved runs of both frozen tests (`scripts/bench/decision_items.py`; 161 items, sha256 b419461f…):
evidence kind of a quoted passage (121 unique record-and-quote pairs; gold: the dossier's v1 annotation, six tool
kinds only; known to be 75% exact on a blind relabelling, and 76% company_assertion) and propose or decline a test
(40 cases; gold: `test_warranted`, 32 propose and 8 decline). Arms: Tiny Aya Global bf16 (the evaluated file) with no
adapter, with the version 1 adapter and with the version 3 adapter, one llama-server process, answers read from the
option letters' log-probabilities at the first reply token (`scripts/bench/decision_logits.py`,
`jobs/decision_logits.sbatch`). Compared with the agent's own choices in the runs (evidence kind: version 1 72% over
choices, final system 80%; test: the agent never declines, 0 of 8 decline cases) and the majority class.
Reported: accuracy, recall per class, expected calibration error, accuracy and coverage when abstaining below 0.5,
0.7 and 0.9 confidence. Reading rule: a typed head is worth training (the next step) only if the zero-training
letter-logit answer already matches or beats the agent's own choice on a task, or its confidence ranks its errors
(accuracy rises with the threshold). This is a method check on the research base; the product base comes from the
model screen (gate 3).

**Result (job 773673).** Evidence kind, 121 items (majority class 76%; the agent's own choices 81% per item for
version 1 and 79% for the final system): letter logits from the base model **81.0%**, expected calibration error
**0.059**; with the version 1 adapter 73.6% (0.133), with version 3 77.7% (0.091). The base model's confidence ranks
its errors: answering only at confidence 0.7 or more keeps 81% of items at 90% accuracy, at 0.9 or more 60% of items
at 97%. Recall is high for company assertions (96%) and low for the rare kinds (independent study 38%, market fact
46%, regulation and analogy 0 of 5). Test choice, 40 cases: every arm proposes a test in all 40 (80% accuracy, the
majority class), so 0 of 8 decline cases, the same failure as the agent. By the registered reading rule, evidence
kind passes (the zero-training answer matches the agent and its confidence ranks its errors), so a trained typed
head is worth building there, with abstention above a confidence threshold; test choice fails, which agrees with the
diagnosis that it needs decline examples in training, not a different readout. The adapters make the letter readout
worse, so the typed head should sit on the base model's weights, not on top of the agentic LoRA. Caveats: 121 items,
gold labels 75% exact on a blind relabelling, and only 8 decline cases. Files: `reports/decision_logits/`.

## 2026-11-19: model screen, round 1 (gate 3), registered before it runs

Four candidate bases with a commercial licence, prompted and not fine-tuned: Granite 4.2 8B,
Qwen3.5-9B, Gemma 4 12B (instruct) and Qwen3.5-4B, each as the maker's or Unsloth's Q8_0 GGUF, checked by sha256
(`jobs/screen_bases.sbatch`). Plus Tiny Aya Global bf16 as the reference. The unchanged environment, the 15
development cases (the six validation companies) and 3 attempts each, in two setups: the staged prompt alone (as the
Tiny Aya base arm ran) and the staged prompt with the final system's decoding guards (no repeats, quote menu, resampled
repeats, step budget, grounded beliefs, evidence first). Development cases only: no test set is touched.

Measured first, mechanically: task success (finished investigations), tool-call accuracy (accepted over all calls),
calls per finished investigation, stop reasons. Blind quality on the finished runs follows with the same two judges.
Reading rule for round 2: the two bases with the most finished investigations under the guards go on to fine-tuning
on the Command A+ rows (the only teacher data cleared for commercial training), provided at least one of them beats
the Tiny Aya reference in the same setup; if none does, the screen says prompting alone is not enough and every base
is fine-tuned before choosing. Reference points: on these cases Tiny Aya's base arm finished 0 of 15 (one attempt)
and the final system 45 of 45.

## 2026-11-19, 01:40: screen round 1, mechanical result, and round 2 started

Round 1 on the development cases, 45 runs per arm, not fine-tuned (`experiments/screen/`): Qwen3.5-9B finished 45 of 45
with the staged prompt alone and 45 of 45 with the guards (tool-call accuracy 99% and 98%, about 20 calls per finished
investigation); Qwen3.5-4B 37 of 45 alone and 45 of 45 with the guards (93%, 98%); Granite 4.2 8B 9 of 45 alone;
Tiny Aya Global 2 of 45 alone and 5 of 45 with the guards. For comparison the fine-tuned final system finished 43 of
45 on the same cases (92% tool-call accuracy, 43 calls per finished investigation). Gemma 4 12B's first run is void:
every reply began with an empty channel marker (`<|channel>thought<channel|>`) that the client did not strip, so no
call parsed; the client now strips it and Gemma is being rerun. Blind quality is being judged by one judge, a new
entry `codexsol170` (gpt-6-sol on the installed Codex CLI 0.170.0, because the pinned 0.166.0 binary is no longer on
the laptop; qualified 20 of 20 on the same 40 packets), on every packet of the comparison including the final
system's, so no judgments from two CLI versions are mixed.

By the registered rule the two bases with the most finished runs under the guards go to round 2: Qwen3.5-9B and
Qwen3.5-4B (both 45 of 45, both above Tiny Aya's 5). Round 2 trains each on version 1's recipe and rows
(`jobs/train_base.sbatch`), with gradient checkpointing and `enable_thinking: false` in the chat template (Qwen3.5's
template otherwise opens a thinking block, which would not match how the server prompts it). A 4-step smoke run on
Qwen3.5-4B passed: every weight loads as a text model, 3,942 rows with none over 8,192 tokens, 13.5 GB peak, 16 s per
step, and the adapter converts to GGUF (496 tensors).

**Decision readout on the round-2 bases (19 November).** The same 161 items, letter logits, no adapter, thinking off in
the chat template (a first try without it read the thinking marker instead of a letter and is discarded). Evidence
kind: Qwen3.5-9B 83.5% (calibration error 0.112; at confidence 0.9 or more, 85% of items at 90% accuracy), Qwen3.5-4B
81.8% (0.093; 73% at 91%), against Tiny Aya's 81.0% (0.059; 60% at 97%) and the agent's own 79 to 81%. Test choice:
both propose in every case, as every arm so far. Files: `reports/decision_logits/decision_qwen3.5-*.json`.

## 2026-11-19, 03:20: screen round 1, blind quality

One judge (`codexsol170`, qualified 20 of 20), 127 packets covering 180 runs: the final system and the three bases in
the guards setup, 45 runs each, blind to the arm, on the 15 development cases (`experiments/screen/judging/`, the key
kept outside the repo). Mean score on the 0 to 3 rubric: Qwen3.5-9B 2.13, Qwen3.5-4B 2.01, the fine-tuned final system
1.88, Tiny Aya Global (prompted) 0.88. Paired by run against the final system, with a 95% bootstrap interval:

| Arm, prompted with the guards | Minus the final system | Companies ahead (of 6) |
|---|---|---|
| Qwen3.5-9B | +0.25 [+0.14, +0.35] | 6 (Neumann +0.01) |
| Qwen3.5-4B | +0.14 [−0.03, +0.31] | 4 |
| Tiny Aya Global | −1.00 [−1.11, −0.88] | 0 |

By dimension, Qwen3.5-9B's gain is largest exactly where version 1 is weakest: recommendation 1.71 against 1.07,
evidence judgement 1.60 against 1.22, distinct theories 2.87 against 2.47. It is lower only on problem framing (2.02
against 2.18). Qwen3.5-4B has the best experiment design (1.53) and recommendation (1.73).

Reading: a newer base with a commercial licence, prompted, already beats the fine-tuned 3.35B system on these cases,
and the base model, not the fine-tuning, accounts for most of the difference. Limits: one judge, development cases
that informed the design, 15 cases. So round 2's question changes: the fine-tuned Qwen adapters are compared against
the same Qwen base prompted with the guards, not only against version 1. If fine-tuning does not beat its own prompted
base, the product ships the prompted base and the training effort moves to the typed decision steps and better teacher
data. Gemma 4 12B finished 45 of 45 in both setups after the client fix and is being judged the same way (17 packets);
Granite 4.2 8B finished 9 of 45 with the guards too (36 stopped on repeated errors) and is not judged.

## 2026-11-19, 04:00: Gemma judged, adapter serving confirmed, training made faster

- **Gemma 4 12B** (guards, 45 runs, 17 packets, the same judge): 1.89, level with the final system (+0.01 [−0.10,
  +0.13]) and below Qwen3.5-9B (−0.24 [−0.35, −0.12], lower at all six companies). Qwen3.5-9B stays the lead base.
- **LoRA on Qwen3.5 in llama.cpp works.** The 4-step smoke adapter loads (`/lora-adapters` lists it) and changes the
  first tokens' log-probabilities by up to 0.098 at scale 1 against 0 (`jobs/adapter_load.sbatch`, job 774147). The
  greedy text does not change, as expected from four steps. So trained adapters can be screened through the server.
- **Training speed (Hatem: "yes start all the options").** The 9B run continues unchanged (about 23 s per step, 1,971
  steps, about 12 hours left). The 4B run moves to the second account, where it does not queue behind the 9B, and
  trains without gradient checkpointing (`GC=0`); if it runs out of memory it is resubmitted with checkpointing and
  resumes from its last checkpoint, which does not change the arithmetic. A separate test measures Unsloth on
  Qwen3.5-4B against the current trainer, same rows, LoRA layers (now listed per model type, including the
  linear-attention projections), seed and checkpointing (`jobs/unsloth_qwen.sbatch`); it is adopted for later runs only
  if its losses track the current trainer's and its adapter converts to GGUF.

## 2026-11-19, 04:40: Unsloth on Qwen3.5 adopted; the 9B run lost to a full home quota and resumed

- **Unsloth fair test on Qwen3.5-4B** (job 774214; 160 rows, 30 steps, the same LoRA, seed, chat-template options
  and standard gradient checkpointing; Unsloth 2026.11.6 with torch 2.11.0+cu128 and transformers 5.17.0): median
  seconds per step after step 10, current trainer 17.2, Unsloth 4.0 (4.3 times faster); peak memory 13.9 GB against
  11.6; the same 32,464,896 trainable parameters; losses agree (first three 0.208/1.009/0.428 against
  0.208/1.008/0.428, last three 0.180/0.859/0.797 against 0.159/0.855/0.800); both adapters convert to GGUF at the same
  size. It passes the rule of 11 November, so round 2 trains with Unsloth from here (`UNSLOTH=1` in
  `jobs/train_base.sbatch`): Qwen3.5-9B on the second account (job 774260) and Qwen3.5-4B (job 774270).
- **Training without gradient checkpointing gave nothing measurable** on the 4B (about 17 to 20 s per step against 17.2
  with it); that run was stopped at step 115 in favour of the Unsloth run.
- **The current-trainer 9B run (774009) died at step 251 (03:26, exit 120)** because Hatem's 50 GB home quota filled:
  the first Unsloth install there (job 774156) downloaded a CUDA 13 torch into home and the pip cache. Freed by
  removing only what that install created (`env_unsloth` and the pip cache); the run resumes from checkpoint 250 as
  the reference for the Unsloth 9B (job 774269). Environment installs now use `--no-cache-dir` and keep the project's
  torch build.

## 2026-11-19, 08:30: Qwen3.5-4B fine-tuned with Unsloth; adapter in the screen

- **Training (job 774270, second account, code 6cf2f44):** the full round-2 recipe (3,942 Command A+ rows plus 51
  corrections, 2 epochs, 1,971 steps, LoRA r16 on all linear layers including the linear-attention projections) in
  3.7 hours with Unsloth; median 4.9 s per step, peak 11.9 GB. Held-out loss (240 rows, six validation companies)
  0.402 at step 50, 0.326 at the end, still flat over the last 400 steps, so no sign of overfitting. The adapter
  converts to GGUF (65 MB, sha256 fcf98370…). Report: `experiments/screen/training/qwen3.5-4b-unsloth_report.json`.
- **Screen (job 774589):** the adapter on the same Q8_0 base as round 1, the compact prompt it was trained in, the 15
  development cases, 3 attempts, with and without the guards; then blind judging with the same judge. Bar, set before
  the result: the fine-tuned 4B must beat prompted Qwen3.5-4B with guards (2.01) and should beat prompted Qwen3.5-9B
  (2.13) to justify the smaller base.
- **Qwen3.5-9B with Unsloth (job 774260):** the same recipe in 4.6 hours (median 6.0 s per step against about 18 for
  the current trainer's reference run, which is still going), peak 22.7 GB. Held-out loss 0.375 at step 50, 0.307 at
  the end, lowest at the last step. The adapter converts (87 MB, sha256 b4223065…). In the screen as job 774684, same
  setup as the 4B.

## 2026-11-19, 10:40: fine-tuned Qwen3.5-4B fails the round-2 bar

- **Screen (job 774589):** with guards 32 of 45 runs finished (prompted 4B: 45), 158 refused calls (13). The calls
  parse; the failures are behaviour. The model repeats calls (median 41 model turns against 18), and at Hellberg it
  keeps citing a simulated result in `finish`, which the environment rejects until the run stops on repeated errors
  (10 of the 13 unfinished runs). Without guards 8 of 45 finished.
- **Blind quality (codexsol170, 40 packets, development cases):** 1.96. Against prompted Qwen3.5-4B with guards
  −0.05 [−0.23, +0.12], so it does not pass the bar; against the final system +0.08 [+0.01, +0.17]; against prompted
  Qwen3.5-9B −0.17 [−0.28, −0.05]. Reports: `experiments/screen/judging/report_qwen4bft_vs_*.json`.
- **Where it moved (fine-tuned against prompted, mean dimension scores):** problem framing 2.20 against 1.80,
  assumptions and predictions 2.78 against 2.47, seeking challenge 1.93 against 1.73; but the recommendation fell to
  0.89 from 1.73 (the final system scores 1.07), causal mechanism to 2.36 from 2.73 and revision to 1.96 from 2.33.
- **Reading:** the rows carry the teacher's procedure into Qwen as they did into Tiny Aya, and the teacher's weak
  recommendation with it: both fine-tuned models land near 1 on the recommendation. This supports the plan's
  diagnosis that the ceiling is the teacher data, not the base size. It is one judge on development cases, so it
  decides only that this 4B adapter is not adopted. The fine-tuned 9B (job 774684) is judged under the same rule.

## 2026-11-19, 12:10: fine-tuned Qwen3.5-9B level with the prompted 9B; neither fine-tuned base passes round 2

- **Screen (job 774684):** with guards 36 of 45 finished (prompted 9B: 45), 89 refused calls (14), median 35 model
  turns (20). The same habits as the 4B, milder: repeated calls, and four runs stopped on citing a simulated result.
- **Blind quality (codexsol170, 31 packets):** 2.13. Against prompted Qwen3.5-9B with guards +0.00 [−0.13, +0.13],
  so it does not pass the bar (it must beat the prompted base); against the final system +0.25 [+0.12, +0.39]; against
  the fine-tuned 4B +0.17 [+0.06, +0.28]. Reports: `experiments/screen/judging/report_qwen9bft_vs_*.json`.
- **Dimensions, fine-tuned against prompted 9B:** experiment design 1.60 against 1.27, problem framing 2.29 against
  2.02, evidence judgement 1.69 against 1.60; recommendation 1.27 against 1.71 and revision 1.96 against 2.33.
- **Decision:** round 2 adopts neither adapter. The lead configuration stays prompted Qwen3.5-9B with the guards (no
  training, 2.13). On both bases the rows raise the procedure steps and pull the recommendation and revision down
  toward the teacher's level, so the next round changes the data, not the base: recommendation and revision rows
  that are better than the teacher's (human-corrected or from a stronger, commercially usable teacher), finish
  examples that keep simulated results out of the cited evidence, and fewer repeated calls in the rows. Adapters
  stay on the second account as references.

## 2026-11-19, 12:50: round 3a, the 9B adapter routed by stage (rule set before the run)

The fine-tuned 9B gained on framing and test design and lost on the recommendation and revision. The runner already
switches adapters per turn by stage (`--lora-route`, 13 November), so one arm keeps the adapter for every stage up to
the test and the position-free steps, and serves the prompted base for the stages that write beliefs, revisions and
the recommendation: `default=0,position=none,update=none,conclude=none`. Two arms, guards on, the 15 development cases,
3 attempts: the compact prompt the adapter was trained in, and the staged prompt the prompted 9B scored 2.13 with.
Same blind judge. Adopted only if an arm beats prompted Qwen3.5-9B with guards (paired interval above 0); otherwise
the prompted base stays.

## 2026-11-19, 13:00: round 3b, recovery rows built by rule (rule set before the run)

The teacher rows hold no repeated call and no simulated citation, so filtering them changes nothing; the students'
two habits come from never having seen a refusal of that kind and what follows it. `src/aemon/rows/recovery_rows.py`
replays each training episode through the tools and, at chosen turns, gives a copy of the investigation the student's
mistake first: the teacher's previous call again (refused as a repeat, or because its stage has closed, or for lack of
searches) or, at the finish, the teacher's finish with a simulated source it read added to the evidence (refused as
synthetic_as_evidence). The context is the state after that refusal; the target is the teacher's own next reply,
accepted on the copy. No model writes anything. 401 rows from 158 training episodes (85 simulated finish, 316 repeat,
at most 2 repeat rows per episode, seeded by episode id; validation companies excluded), sha256 711893ad…; with the 51
correction rows, the extras file `extras_39d147a.jsonl` (sha256 1110a555…).

Qwen3.5-9B is retrained with Unsloth on the same rows and recipe with these extras (job below), and screened like
round 2 (compact prompt, guards, blind judge). Success: more finished runs than the round-2 adapter (36 of 45) and
fewer refusals (89); adopted only if it beats prompted Qwen3.5-9B with guards. If round 3a's stage route wins, the two
are combined afterwards.

**Round 3a, staged-prompt arm (job 775228), 13:25.** 45 of 45 finished, 12 refused calls, median 25 turns; 954 turns
written with the adapter, 129 (position, update, conclude) by the prompted base. Blind quality 2.00 (18 packets):
against prompted Qwen3.5-9B −0.13 [−0.26, −0.02], against the fully fine-tuned 9B −0.13 [−0.28, +0.00], against the
final system +0.12 [+0.05, +0.19]. Routing removes the refusals but not the quality loss: the recommendation recovers
only to 1.51 (prompted 1.71, fine-tuned 1.27), and experiment design falls to 1.00 (1.27 and 1.60), the adapter
working under a system prompt it was not trained with. Not adopted. The compact-prompt arm is still running.

**Round 3a, compact-prompt arm (job 775227), 14:25.** 31 of 45 finished (11 repeated errors, 3 turn limit), 131
refused calls, median 38 turns. Blind quality 2.16 (36 packets), the highest of any arm so far, but against prompted
Qwen3.5-9B +0.03 [−0.10, +0.15] and against the fully fine-tuned 9B +0.02 [−0.10, +0.15]: not above zero, so not
adopted under the rule. Against the final system +0.28 [+0.16, +0.39]. It keeps the adapter's gains on framing (2.51
against 2.02), experiment design (1.71 against 1.27) and assumptions (2.80 against 2.69), but the prompted base under
the compact prompt writes weaker revisions (1.41 against 2.33 under the staged prompt) and recommendations (1.49
against 1.71). So the routed design is worth carrying forward only with fewer refusals, which is what round 3b's
recovery rows target; the combination (3b's adapter, this route) is the next screen once 3b finishes.

## 2026-11-19, 15:00: Lexsi next stage; student moves from Tiny Aya Global (3.35B) to Aya Expanse 8B

We qualified for the next Lexsi stage. Hatem: "let's put the startup thing aside, lexsi is still on", "we still need
to abide by their rules, I want to switch from 3B tiny aya to 8B tiny aya", "and do the actual training". There is no
8B Tiny Aya (every Tiny Aya on the Hub is 3.35B); the 8B Aya with a text model is Aya Expanse 8B (CohereLabs,
revision 5062468b, model type `cohere`, CC-BY-NC-4.0 like Tiny Aya), so it is the new student. The startup jobs
(round 3b retrain and its screens) were cancelled to free the GPUs.

Recipe: version 1's, unchanged except the base: the Command A+ rows and the 51 corrections, LoRA r16/alpha 32 on every
linear layer (q, k, v, o, gate, up, down), 2 epochs, the same validation companies and seed, AgentTune's distillation
trainer, with Unsloth building the model and LoRA (19 November 04:40). First a CPU probe (jobs/probe_load.sbatch):
every weight loads, the LoRA layers, row lengths in its tokenizer against its 8,192-token context, the chat template.
Then the adapter is converted to GGUF and screened against version 1 (1.88) and the prompted Aya Expanse 8B on the
development cases with the guards, same blind judge.

## 2026-11-19, 16:50: Aya Expanse 8B probe passed; Stage 2 training and the rule (set before any result)

Probe (job 775854): `CohereForCausalLM`, no missing, unexpected or mismatched weights; LoRA on all linear layers wraps
224 modules (q, k, v, o, gate, up, down in 32 blocks), 41,943,040 trainable parameters; Cohere's chat template. The
probe's row-length line is wrong on transformers 5 (`apply_chat_template(tokenize=True)` returns an encoding, so it
counted its 2 keys); counted again with the Aya Expanse tokenizer on all 4,302 rows: median 2,976 tokens, 99th
percentile 5,146, longest 6,033, none over the 8,192 context. The experiments' model files (Qwen runs and screen
logs) were removed on both accounts; Tiny Aya's models and runs are kept.

Two runs, one per account, version 1's recipe with Unsloth building the model inside AgentTune's distillation trainer:
A (Nour's, job 775855) on version 1's data (Command A+ rows and the 51 corrections); B (Hatem's) on the same plus the
401 recovery rows built by rule (13:00 entry). Each is screened on the 15 development cases, 3 attempts, compact
prompt, guards, context 8,192, the same Q8_0 base file for every Aya Expanse arm (bartowski, sha256 75e5bfef...), and
judged blind by codexsol170 with the earlier arms. Prompted Aya Expanse 8B (job 775856, staged prompt, with and
without guards) is the base arm. Rule: a variant goes on to the held-out test set only if it beats version 1 (Tiny Aya
3.35B, 1.88 on these cases) with a paired interval above 0 and finishes at least as many runs as version 1; if both
pass, the higher mean goes.

**Review before the overnight runs (17:05), and what changed.**
- *Third-party Q8_0 GGUF: its chat template and BOS handling are unchecked, and version 1 ran in bf16.* Adopted: every
  Aya Expanse arm is now served from a bf16 GGUF converted in the job from the pinned Hugging Face revision with our
  llama.cpp, as version 1's Tiny Aya file was (`jobs/screen_bases.sbatch`, `HF_REPO`/`HF_REV`), and
  `scripts/bench/template_check.py` must find the server's tokens for a training row's context identical to training's
  (template with generation prompt, no added special tokens) before any run, or the job stops. The queued Q8_0 screens
  (775856, 776095) were cancelled and resubmitted this way.
- *A failed runner was hidden by `|| true`, and a stale result could be read.* Fixed: old outputs are removed first and
  a non-zero exit is reported and skips that arm's summary.
- *8,192 tokens may run out on long investigations.* Measured on earlier screens: prompted Tiny Aya (whose context is
  also 8,192) stopped at the context limit in 31 of 45 runs; the fine-tuned Qwen runs peaked at 6,842 to 8,036 prompt
  tokens. Version 1 lives under the same limit, so the comparison is fair; context-limit stops are reported as their
  own stop reason, not hidden among unfinished runs.
- *Unsloth support for `cohere` and the LoRA conversion are untested.* Unsloth 2026.11.6 ships a Cohere model file and
  llama.cpp's LoRA converter uses the same architecture table as its model converter, which handles Command R and
  Aya Expanse. A failure at model load stops the job in minutes; a conversion failure leaves the PEFT adapter saved, to
  convert on its own. No separate smoke run, since the queue is full and it would cost a place.
- *Recovery rows carry the unguarded state, while screens add guard fields (budget, evidence ledger).* True, and the
  same holds for every teacher row, which version 1 was trained on and served with guards; recorded as such.
- *The rule could pass a variant that only beats version 1 while the prompted 8B is as good.* Adopted: a variant goes
  on to the test set only if it beats both version 1 and prompted Aya Expanse 8B (paired intervals above 0).

## 2026-11-19, 20:20: decision model in the loop, and seeds (rules set before any result)

Hatem: "we also need to integrate decision model ... we need to discover if decision models will also help"; "i also
want to try multiple seeds, to make sure that the results are trusted". Plan reviewed independently first.

- **decide_kind** (`src/aemon/agent/decision.py`, hook in `loop.py`): on an `assess_evidence` call whose kind is not
  already fixed by `evidence_first` (company claims are), the base weights (adapter at scale 0 for that request) score
  the six kinds by their letters' log-probabilities; it replaces the agent's kind only if every letter is among the
  candidates and the renormalised confidence is at least 0.9 (fixed now, not tuned on the labelled items). The model's
  text stays in its turn; the decision, with the executed arguments, is recorded on the turn and on the call, and
  prefix replay re-applies it. Unit tests: decide, abstain, single-option skip, record, replay.
- **Test**: each fine-tuned adapter screened in one job, twice on the same code and seeds: guards, and guards plus
  decide_kind, every agent request naming its adapter (`ROUTE=default=0`), after a check that a scale-0 decision request
  leaves the next agent request's log-probabilities unchanged; then the 161 labelled items offline. Prompted Aya Expanse
  8B the same way, without the isolation check. Same bf16 base, same blind judge.
- **Seeds**: training A is repeated with seeds 11 and 13 (seed 7 running), each screened the same way, so every effect
  is reported per training seed and as the mean over seeds with the seed-to-seed spread. Within a seed, attempts 0 to 2
  are three sampling seeds per case.
- **Rule**: decide_kind helps if, pooled over the three training seeds, the paired difference (on minus off, per run) has
  a 95% interval above 0, the sign is the same in at least two of three seeds, and finished runs do not fall. The
  variant rule of 16:50 is applied to the mean over seeds; a single seed's result is reported as such.

**Prompted Aya Expanse 8B, judged (20:30).** Job 776344 (bf16 converted in the job, template check passed: 1,126
tokens identical, one BOS), staged prompt with guards: 27 of 45 finished, 15 at the context limit, 3 repeated errors.
Blind quality (codexsol170, 30 packets) 1.41: against version 1 (fine-tuned Tiny Aya 3.35B) −0.47 [−0.59, −0.36],
against prompted Tiny Aya +0.52 [+0.41, +0.65]. So the larger Aya base alone is far better than the small one, but well
below the fine-tuned small one; the gap to version 1 is largest on revision (0.70 against 2.00), distinct theories
(1.56 against 2.47) and the recommendation (0.62 against 1.07). Fine-tuning is what the 8B is missing, which is what
runs A and B test. Reports: `experiments/screen/judging/report_ayaexp8b_vs_*.json`.

## 2026-11-19, 20:30: ablations (rule set before any result)

Hatem: "explore to implement multiple ablations as well to test the model better". Plan reviewed independently.
Reference: adapter A (seed 7), compact prompt, the six guards. Each arm changes one thing, on the same server, base,
cases and attempts (`jobs/screen_bases.sbatch` arm names; `DRY=1` prints each arm's runner arguments): `none` (no
guards), `minus_quote` (quote_menu with the evidence_first it carries), `minus_repeats` (no_repeats with
resample_repeats), `minus_budget`, `minus_ledger` (grounded_beliefs), `routed` (adapter off for position, update,
conclude), `staged_prompt`, `decide` (own rule, 20:20). Training arms: prompted 8B, A without correction rows
(`EXTRA_SHARE=0`), B (recovery rows), seeds 11 and 13. General ability: base against A on the MMLU and ARC items
(`jobs/retention_aya.sbatch`). Guard groups that the reference's records show almost never acting are reported as such
and not screened.

Measures: the blind judge score paired by run against the reference, the interval from resampling whole cases; finished
runs as a per-case paired difference; stop reasons with the context limit apart; refused calls; turns; how often each
step acts; and, as diagnostics only, evidence-kind accuracy of accepted assessments against the dossier (company claims
and third-party sources apart) and propose/decline against `test_warranted` (`scripts/bench/ablation_table.py`).
Primary rows: prompted 8B, B, no guards, decide. Rule for a primary row: a part earns its place if removing it lowers
the judge score with the interval below 0, or lowers finished runs by at least 5 of 45 without a judge gain; otherwise
inconclusive at 15 cases. The other rows are exploratory and describe direction and size only. The configuration chosen
goes once to the held-out test set.

First reading of the table on earlier screens (a check of the script): third-party evidence kinds are right in only 23
to 27% of accepted assessments in every arm (Qwen and Aya, prompted and fine-tuned), against the dossier annotation;
company claims are fixed by evidence_first. So decide_kind has room to act there.

## 2026-11-19, 20:45: inference cost bench (registered before it runs)

Hatem: "can we optimize inference cost after training to make it cheaper than a ready model?" Version 1 costs $0.032 per
investigation self-hosted, one at a time (66 s on an A100 slice, $1.76/h); Claude Haiku 5.5 measured $0.0084. To beat
Haiku at that price, one GPU must complete more than about 210 investigations an hour. `jobs/inference_bench.sbatch`
merges adapter A into the base (`scripts/bench/merge_adapter.py`), converts it to bf16 and 8-bit GGUF and quantizes it
to Q4_K_M (quantizer built by `jobs/llama_tools.sbatch` from the server's llama.cpp release), and serves each with 1, 4,
8 and 16 investigations at once on the 15 development cases with the guards. The client now records the prompt tokens
the server actually computed (`prompt_processed`), so the share taken from its prompt cache is measured.
`scripts/bench/inference_summary.py`: investigations per GPU hour, cost per investigation (and per finished one) at the
three GPU prices of the version 1 table, cache share, finished runs and refused calls. A setting counts only if it
finishes at least as many runs as bf16 at one slot, within 3 of 45; the fastest such setting then gets the blind judge.
Speculative decoding from the prompt is next if the server build supports it (the tools job prints its flags).

## 2026-11-19, 21:20: Stage 2 deliverable, two reviews of the plan, and Hatem's choices

Stage 2 (organisers' email): a short paper in the latest EMNLP template, under 6 pages plus up to 6 pages of appendix,
due 24 November 11:59 PM AoE (25 November 12:59 Milan). Two outside reviews of the plan were checked against the repo;
what holds:
- **Campaigns are kept apart.** 1.48 against 0.65 is the frozen first test, mean of two judges; 1.88, 0.88 and 1.41
  are development screens with one judge (codexsol170). They never share a column.
- **Neither frozen test is fresh.** The first was diagnosed (`docs/FINAL_TEST_DIAGNOSIS.md`) and the second was run and
  discussed; a new run on either is a retest. Hatem: build a small fresh test set of new companies, frozen by digest
  before any run.
- **Fine-tuning is isolated by matching the scaffold.** The 1.41 arm used the staged prompt (guards, no decision model);
  the fine-tuned arms use the compact prompt. The prompted 8B pair (guards, decide) is resubmitted on the compact prompt
  (job 776846); the staged result stays as a prompt variant. decide_kind reads the base weights and never the dossier's
  kind annotation (it sees the title, whether the company published the source, and the quote), so its effect is the
  decision model's, not fine-tuning's.
- **B is one seed with 2,172 optimizer steps against A's 1,971**, so B against A is recovery rows plus more training;
  exploratory, with that limitation stated.
- **Cost** is reported per attempted and per finished investigation at each GPU price, beside finished runs and judge
  score; the 210-per-hour bar assumes $1.76/h and Haiku's measured $0.0084.
- Aya Expanse 8B is CC-BY-NC-4.0 (Hugging Face model card, revision 5062468b), as Tiny Aya: fine for the paper, not
  for a commercial product without Cohere's agreement.
Hatem's choices: keep all ablations; Claude as a second judge on the final comparison (paid; cost reported before and
after); start the EMNLP outline now.

**Training A finished (job 775855, 21:20).** 1,971 steps in 4.3 hours with Unsloth, peak 19.7 GB; held-out loss 0.565
at step 50, 0.387 at the end. Adapter converted (`experiments/screen/training/aya-expanse-8b-s7_report.json`). Its
screen (guards, guards plus decide_kind, then the offline items) started at once; seed 11 was requeued behind it so
the decision test is not delayed by a training run.

## 2026-11-19, 21:30: one round of recovery training from the student's own states (registered before it runs)

Outside advice (pasted by Hatem): the teacher data teaches the procedure more than the judgement; collect the
permitted teacher's actions on states the student actually reaches (DAgger's motivation; no guarantee here). One round,
exploratory, due by Monday 23 November 10:00 or reported as not run:
1. Student A (seed 7) on 20 training-company base cases drawn with a fixed seed from the 57 in A's rows outside the
   validation companies (a123, blackdecker, carrier, festool, gore, illumina, kes, leitz, lenzing, maglite, martek,
   masimo, nalgene, netafim, osram, oxo, resmed, sigvaris, sma, stihl), 3 attempts, no guards so its loops show
   (`jobs/screen_bases.sbatch`, `CASES`, arm `none`).
2. `aemon.teacher.corrections states` on those runs (loop starts: a refused repeat, a third read of one source, a second
   refusal in a row; training companies only), then `ask` with Command A+ (`jobs/command_a_plus.sbatch`, correction
   batch, one 80 GB slice), kept only if the tools accept the answer, it repeats nothing and its justification names
   something in the state it acts on; `rows` with provenance.
3. A retrained on its rows plus these corrections (same recipe, seed 7), screened with guards on development, judged.
Nothing written by the judge models is trained on. Skill-focused contrastive cases, preference training and agent RL
are future work in the paper.

## 2026-11-19, 21:45: test set 3 frozen (before any run, and before A's screen results were read)

Five companies, none in any case file, training-row file or proposal list (`data/dossier/raw/heldout3/excluded_companies.txt`)
and none in the product category of a development or test company: Eberspächer Gruppe (vehicle and parking heaters),
Gühring KG (cutting tools), Krones AG (beverage filling lines), U.I. Lapp GmbH (industrial cables; Lapp Mobility sells
EV charging gear), MULTIVAC Sepp Haggenmüller (packaging machines; MULTIVAC home was a household chamber sealer).
Research by five agents (web search and fetch only, verbatim excerpts, a mix of company and third-party sources,
`data/dossier/raw/heldout3/h3_*`), then `aemon.data.verify_sources` against the live pages: 110 records, 99 verified
and admitted (Eberspächer 20, Gühring 17, Krones 22, Lapp 22, MULTIVAC 18); 11 not found or not fetchable and dropped,
never edited. Each company has a base case and a `-new-evidence-irrelevant` case (as test set 2): 10 cases. Kinds use the
tool's six kinds; they are annotations for diagnostics, written by the research agents, never trained on.

Premise records (what the `existing_offering` check needs the agent to read one of) were set to the records that show
each company's existing reach to individual or small buyers, since that is the easy false premise the check is about:
Eberspächer's consumer pre-heater site, dealer search and a retailer's listing; Gühring's DIANOZ maker nozzle and its
reseller, and its B2B shop; Krones' MicroCube, Craftmate and Krones.shop (it sells nothing to consumers); Lapp
Mobility's end-consumer page, private checkout and home wallbox; MULTIVAC home and the tabletop machines' users.

Checks (`scripts/bench/test3_checks.py`): no test set 3 company, record or case id in any case file, row file, teacher
report or run report. Searchability, with queries modelled on the agent's own development searches and the company's
short name: every case reaches a premise record and at least four other records, the bar the earlier sets meet (the
hand-built first test reaches five or more everywhere; test set 2 reaches at least four, four of its companies exactly
four; Gühring here reaches four). Earlier freezes unchanged (digests recomputed).

Freeze (`docs/test3_freeze.json`, `tests/test_test3_freeze.py`): digest 8570f7a6…, 5 companies, 10 cases, 99 records.
Run once, on Monday 23 November afternoon: the configuration chosen on development only (adapter, guards, decision model
if adopted), the prompted Aya Expanse 8B with the same scaffold, and version 1 (Tiny Aya 3.35B); 3 attempts per case,
30 runs per arm; judged blind by codexsol170 and by Claude (Stage 1 settings and qualification), reported per judge and
as the mean, paired by run, intervals by resampling cases; nothing about test set 3 is changed after this entry.

## 2026-11-19, 23:41: test set 3 refrozen at 12 companies with signed evidence (before A's scores were opened)

Why: with 5 companies the company-level 95% interval (t on 4 degrees of freedom) is about ±0.43 for a ±0.35 spread of
paired company differences; at 12 about ±0.22. Two outside reviews (pasted by Hatem) asked for 12 companies chosen by a
written rule, and for supporting and contradicting evidence so belief revision is tested. An interval crossing 0 on the
final run is reported as inconclusive (registered now).

Selection (`data/dossier/raw/heldout3/selection_rule.md`, committed 23:15:39 and amended 23:15:53, before any research
agent ran): B2B-first manufacturers, roughly EUR 0.3 to 15 billion revenue, not in any case file or proposal, not in any
development or test company's product category (strikes recorded with reasons), 12 sectors, at least 5 countries; a
seeded draw over the vetted pool, then the country rule (Tomra replaced Interroll). Added: Kardex (storage automation),
Nabtesco (gear reducers, automatic doors, welfare products), Biesse (woodworking machinery), Brembo (brakes), Rieter
(spinning machinery), Sika (construction chemicals), Tomra (reverse vending and sorting). Countries: Germany,
Switzerland, Italy, Japan, Norway.

Dossiers: seven research agents, the same instructions as the first five plus "no pages about future decisions";
`aemon.data.verify_sources` against the live pages; 152 records, 131 verified and admitted (Kardex 19, Nabtesco 20,
Biesse 20, Brembo 16, Rieter 20, Sika 20, Tomra 16); 21 not found or not fetchable, dropped unedited. Premise records
are each company's existing reach to individual or small buyers, trimmed to verified records; for Rieter, which sells
nothing to consumers, the record that it sells to more than 3,000 spinning mills was added as the first premise (its
other premises, a reference book, a calculator app and a mills' webshop, are not reached by the agent-style queries).
Brembo, Tomra and Nabtesco read end to end: mixed company and third-party sources, evidence against a consumer move
present in each, no future plans stated as fact.

Signed evidence (`reviews/heldout3_shocks/`): per company one simulated randomized offer test on a narrow mechanism, in
the final test's design: identical record id and title in the favours and undermines cases, counts mirrored (72
against 32 of 400 per arm), "SIMULATED RESULT, NOT REAL DATA" in the record, targets that pick out a theory about the
mechanism and not an unrelated one, and the tools refuse the record as support or as cited evidence (120 of 120
checks). Mechanisms: installation (Eberspächer), durability assurance (Gühring), cleaning burden (Krones),
compatibility (Lapp), running costs (MULTIVAC), upfront cost (Kardex), safety assurance (Nabtesco), programming
complexity (Biesse), trial before purchase (Brembo), learning barrier (Rieter), application difficulty (Sika), return
convenience (Tomra). These are case-author constructions and never trained on.

Checks: no test set 3 company, record or case id in any case file, row file, teacher report or run report; every case
reaches a premise record and at least four other records; earlier freezes unchanged. Freeze (`docs/test3_freeze.json`):
digest 068261a9..., 12 companies, 48 cases (base, irrelevant, favours, undermines each), 230 records. The Monday run:
the configuration chosen on development, the prompted 8B with the same scaffold, and version 1; 2 attempts per case
(96 runs per arm; attempts cut, not companies); two judges; per-company paired differences with t-intervals.
A's guards arm was judged in the background tonight; its scores were not opened before this commit.

**A (Aya Expanse 8B, version 1's data, seed 7), guards, judged (23:45, after the refreeze).** Job 776728, compact
prompt, guards, bf16 base converted in the job, template and adapter-isolation checks passed. 39 of 45 finished
(5 repeated errors, 1 context limit), 146 refused calls, median 35 turns. Blind quality (codexsol170, 45 packets):
**2.02**. Paired by run against version 1's final system on the same development cases (`experiments/grounded/screen2/D.json`,
1.88): **+0.14 [+0.04, +0.24]**, ahead at 5 of 6 companies (Neumann −0.16). Against prompted Aya Expanse 8B on the
staged prompt (a prompt difference, not a matched baseline; the compact-prompt pair is job 776909): +0.61 [+0.50,
+0.72]. Against prompted Tiny Aya +1.14 [+1.04, +1.24]; against prompted Qwen3.5-9B (supplementary, not a Cohere
student) −0.11 [−0.22, +0.00]. Largest gains over version 1: revision 2.30 against 2.00, distinct theories 2.69
against 2.47, evidence judgement 1.42 against 1.22, problem framing 2.38 against 2.18.

Under the rule of 16:50, A does not yet pass: it beats version 1 on quality, but finishes 39 runs against the final
system's 43 (which also routes adapters by stage; A does not). Diagnostic (`experiments/screen/ablation_stage2_partial.json`):
the evidence kind of accepted third-party assessments matches the dossier annotation in 6% of A's (11 of 180)
against 36% of the final system's; that is what decide_kind acts on (its arm, job 776728, follows).

## 2026-11-19, 23:43: training-data experiment and a second teacher (registered before any of it runs)

An outside review (pasted by Hatem) corrected my claim that training-data size is not the bottleneck: falling
validation loss shows the student predicts the teacher better, not that more or better data would stop helping. Four
conditions, all at training seed 7 first with the reference's recipe, seeds 11 and 13 added for any condition that
differs from the reference; reported with supervised tokens and GPU-hours:
- **Reference:** A (version 1's rows and corrections; seeds 7, 11, 13 running or queued).
- **Composition** (`scripts/oneoff/composition_rows.py`, `rows/composition_s7.jsonl`, sha256 a8b199dd...): the same rows
  resampled by skill group with shares proportional to the square root of their current shares, at the reference's
  target-character budget; validation rows unchanged. Shares before and after: theories 0.30 to 0.24, recommendation
  0.22 to 0.20, test 0.18 to 0.18, procedure 0.17 to 0.18, assessment 0.11 to 0.14, revision 0.02 to 0.06.
- **Recovery:** the reference plus Command A+ corrections from the student's own states (21:30 entry).
- **Quantity:** the reference plus new Command A+ investigations on more training companies, collected the same way;
  it needs 80 GB slices for many hours, so it runs last.
Run B's recovery rows are rule-built, a separate source labelled `recovery-rule`, never called teacher demonstrations.

**Second teacher.** Two reviews suggest Qwen as an alternative teacher. Checked on the Hub: Qwen3.8-27B (Apache 2.0,
model type `qwen3_5`, the architecture our llama.cpp build already serves; Unsloth GGUF available) and
Qwen3.5-122B-A10B (Apache 2.0, MoE, needs an 80 GB slice at 4-bit). Lexsi permits other models as teachers while the
trained agent stays Cohere's. First comparison: Qwen3.8-27B (Q8_0 on a 40 GB slice) and Command A+ answer the same
student failure states from the recovery round under the same correction protocol; compared on acceptance by the
tools, the blind judge's view of a sample, and evidence-kind accuracy. Only if Qwen is at least as good does a matched
adapter follow (same states, same token budget, seed 7). Qwen's weights are added to the permitted-teacher list
(`TEACHER_WEIGHTS`) only with its licence recorded, and its rows are tagged with their teacher.

**B trained (job 776343, 00:30).** Aya Expanse 8B on version 1's rows, the 51 corrections and the 401 rule-built
recovery rows (`recovery-rule`), seed 7: 2,172 steps (A: 1,971) in 4.7 hours, peak 20.1 GB; held-out loss 0.575 at
step 50, 0.390 at the end (A: 0.565 to 0.387; the same 240 validation rows). Its screen (guards, then guards with
decide_kind) is submitted by the overnight driver; B stays exploratory (one seed, about 10% more optimizer steps).

**decide_kind at training seed 7, judged (01:01).** Same job (776728), same seeds and code as the guards arm, the
adapter-isolation check passed. Mechanical (`experiments/screen/ablation_stage2_A7.json`): 39 of 45 finished in both
arms; 50 replacements and 11 abstentions over 187 third-party assessments; the evidence kind of accepted third-party
assessments matches the dossier annotation in 54% with the decision model against 6% without (version 1's final
system 36%). Blind quality (codexsol170, 45 packets): 2.04 with decide_kind against 2.01 without, **+0.03 [−0.03,
+0.08]**, higher at 4 of 6 companies; by dimension, evidence judgement 1.60 against 1.42 and problem framing 2.51
against 2.36, the others within ±0.07. Against version 1's final system: +0.16 [+0.06, +0.26]. Under the rule of
20:20 a single seed is reported as such: at seed 7 the effect on quality is inconclusive and its sign positive; seeds
11 and 13 decide. Offline (`experiments/screen/aya-expanse-8b-s7_decision_logits.json`, 161 items): Aya Expanse 8B
base weights 81.8% evidence-kind accuracy (majority class 76.0%), calibration error 0.156, at confidence 0.9 or more
93% of items at 86.6%; with the adapter 81.0%. Test choice: proposes in every case, so it stays out of the loop.

**Fine-tuning isolated: A against the prompted 8B with the same scaffold (01:58).** Job 776909, guards arm:
prompted Aya Expanse 8B on the compact prompt, with the same guards, context, bf16 base and code as A: 4 of 45
finished (39 repeated errors, 2 turn limit), 265 refused calls, most of them a position stated before the favoured
theory was challenged (140) and a simulated result cited in finish (51). Blind quality (codexsol170, 34 packets): 1.29.
A minus it, paired by run: **+0.73 [+0.60, +0.85]**, ahead at all 6 companies (+0.51 to +0.93); finished 39 against 4.
By dimension the gap is largest where Stage 1's student was weakest: recommendation 1.16 against 0.09, revision 2.33
against 0.30, distinct theories 2.69 against 1.38, problem framing 2.36 against 1.40. Against the prompted 8B under
its best prompt (staged, 1.41) the gain is +0.61 [+0.50, +0.72]; both are reported, the matched one as the primary
"does fine-tuning help" row. The decision-model arm of this job follows.

**B judged, guards (02:27).** Job 777413 (same code, base, prompt, guards and checks as A): **45 of 45 finished**,
28 refused calls (A 146), 16 redrawn repeats (A 110), median 39 turns. Blind quality (codexsol170, 23 packets):
**2.19**. Paired by run: against A **+0.18 [+0.09, +0.25]**, ahead at all 6 companies; against version 1's final
system **+0.31 [+0.21, +0.41]**, all 6 companies, finishing 45 against 43; against the prompted 8B with the same
scaffold +0.91 [+0.75, +1.04]. By dimension against A: recommendation 1.84 against 1.16, revision 2.70 against 2.33,
problem framing 2.69 against 2.36, distinct theories 2.96 against 2.69; seeking challenge 1.67 against 1.91 is the
one dimension lower. So at seed 7, rule-built recovery rows both remove the loops and raise judged quality, most of all
the recommendation. B meets the variant rule of 16:50 (amended 21:20): it beats version 1 and the prompted 8B with
intervals above 0 and finishes at least as many runs. It stays exploratory until replicated: one seed, and 2,172
optimizer steps against A's 1,971. Registered now, before more results: B is retrained at seeds 11 and 13, and a
step-matched control trains B's data for exactly 1,971 steps (seed 7), so the recovery rows can be separated from the
extra steps; each is screened with guards and decide_kind like A. The configuration for test set 3 is chosen from
these development results only, on Monday by noon.

**decide_kind on the prompted 8B (same scaffold), judged (03:13).** Job 776909, decide arm: 7 of 45 finished
(4 without), 222 refused calls (265), 14 replacements and 6 abstentions; third-party evidence kinds matching the
annotation 53% (32% without). Blind quality 1.33 against 1.29: **+0.03 [−0.00, +0.08]**, evidence judgement 1.04
against 0.91. The same direction and size as on A (+0.03 [−0.03, +0.08], evidence judgement 1.42 to 1.60): on two
agents the decision model fixes its typed choice and lifts the dimension it feeds, with a small whole-run effect so
far. Seeds 11 and 13 of A and B decide it under the rule of 20:20.

**decide_kind on B, judged (04:06).** Job 777413, decide arm: 45 of 45 finished, 22 refused calls, 61
replacements and 14 abstentions; third-party evidence kinds matching the annotation 46% (14% without). Blind quality
2.20 against B's 2.19: **+0.005 [−0.08, +0.09]**; evidence judgement 1.58 against 1.51; against A with decide_kind
+0.16 [+0.07, +0.23]; against version 1's final system +0.32 [+0.22, +0.41]. So at seed 7 the decision model fixes the
typed choice on all three agents (A, B, the prompted 8B) and moves whole-run quality by +0.03, +0.00 and +0.03, all
with intervals across 0: inconclusive, small either way. Mechanical table: `experiments/screen/ablation_stage2.json`.

**B at training seed 11, guards arm, judged (12:22; decide arm still running, job 778437).** 41 of 45
finished (45 at seed 7), 330 refused calls (28), of them 327 repeats, 255 at one company (Hellberg) and most in five
runs (72, 64, 30, 26, 18). Blind quality 1.97: against B at seed 7 (2.19) **−0.23 [−0.41, −0.06]**; against A at seed
7 (2.01) −0.05 [−0.19, +0.09]; against version 1's final system +0.09 [−0.06, +0.23]; against the prompted 8B on the
same scaffold +0.67 [+0.56, +0.77], all six companies. Reading: the fine-tuning effect replicates at a second seed;
the recovery rows' effect does not yet. The gap between two seeds of the same data (0.23) is larger than B's gain over
A at seed 7 (0.18), so seed 7's +0.18 is within training-seed variation until the matched comparison (A at seed 11,
B and A at seed 13) says otherwise; the paper states B's gain as a single-seed result. The registered variant rule
is decided on all three seeds, not on seed 7.

**Registered (12:37, before any code or result): a trained decision head for the evidence kind (Hatem's call,
"a model similar to Jev").** The open recipe of arXiv 2610.17205, step 2: Aya Expanse 8B (the pinned revision), LoRA
r16, alpha 32, dropout 0.05 on the seven projections, and a head that is the LM head's rows for the six option letters
(cross-entropy over those six at the answer position, so training starts from today's zero-shot decider). Prompt:
`decision.kind_prompt`, identical to decide_kind's. Data: dossier records of the training companies only (the 93
training scopes; no development, validation, test, test 2 or test set 3 company), kinds in the tool's six: 1,226
records, 749 third-party; items are the excerpt and its longer sentences as quotes. Calibration split: 15% of the
training scopes (seeded, 7), never trained on. Training: 2 epochs, learning rate 1e-4, seed 7. Calibration: one
temperature per arm (zero-shot base and trained head alike), fitted by log-loss on the calibration split. Offline test:
the 121 evidence-kind items (final-test and test 2 companies, already read, never trained on); primary metric
accuracy, then calibration error, and coverage and accuracy at the fixed 0.9 threshold. **Rule for the in-loop run:**
only if the trained head's accuracy is at least 5 points above the zero-shot base's (81.8%) and its calibration error
is no worse, after calibration; otherwise it is reported offline only. In the loop: A at seed 7, decide arm with the
trained head against the existing decide arm, development, one judge. GPU priority: after the seed replications and
test set 3.

**Amended (12:41, before any training or result), after an independent review of the decision-head design.**
(1) Leak: one training record (nilfisk-2025-split) carries the same sentence as a frozen test quote (Tennant); records
sharing any eight-word run with a frozen test quote are now left out, mechanically. (2) Training quotes: instead of
sentences cut from records (a record's label need not fit each sentence), each record gives its excerpt plus the
quotes Command A+ itself chose for it in the teacher rows, the same kind of agent-chosen quote the test items are:
1,316 training items (1,037 excerpts, 279 teacher quotes), 231 calibration items; record list frozen by hash in
`experiments/decider/items_summary.json`. (3) Go rule, stricter: the registered conditions plus a paired accuracy
interval, bootstrapped over records, whose lower bound is above zero (one arm's standard error on 121 items is about
3.5 points, so 5 points alone is about six items). (4) Also reported: accuracy on the 48 third-party items (the only
ones decide_kind acts on; the zero-shot base gets 54% there), per kind, the rate of answers missing a letter among the
top 20 tokens, and the items where the two arms disagree. The 121 items stay a selected, clustered sample: the result
is offline evidence for one choice, not a general claim.

**Judged (13:44): decide_kind on B at seed 11, and A without the correction rows (seed 7).**
*decide_kind, B seed 11* (job 778437): 42 of 45 finished (41 without), 331 refused calls (the same Hellberg loops);
quality 2.03 against 1.97, **+0.06 [−0.06, +0.18]**, evidence judgement +0.20. So far decide_kind is +0.03 (A, seed 7),
+0.005 (B, seed 7), +0.06 (B, seed 11), +0.03 (prompted 8B): the same sign every time, every interval across 0. The
registered pooled verdict waits for A at seed 11 and both at seed 13.
*No correction rows* (job 778242, A's teacher rows alone, seed 7): 37 of 45 finished (A: 39); refused calls 85 (146):
53 repeats (110), 32 simulated results cited as evidence (20). Quality 2.01 against A's 2.01, **−0.00 [−0.14, +0.12]**;
recommendation +0.29, revision −0.22, companies split three each way. Under the registered rule (an interval below 0,
or 5 or more fewer finished runs) the 51 correction rows do not earn their place on judged quality at this seed; what
they were written for moves the expected way (fewer simulated results cited as evidence with them, 20 against 32).
Against the prompted 8B the no-corrections run is +0.72 [+0.55, +0.87]: the fine-tuning effect is the teacher rows.

**Registered (14:05, before A seed 11, either seed 13, the step-matched run or any test set 3 result): how the
final configuration is chosen, how test set 3 is read, and how the remaining comparisons are judged** (two pasted
reviews, adopted).
1. *Eligibility.* Only configurations with judged development results at three training seeds (7, 11, 13) by Sunday
   22 November 23:59 can be chosen: in practice A, possibly B. The recovery-round retrain, the trained decision head
   and the composition run arrive with one seed and are not eligible, whatever they score.
2. *Choice, mechanically.* A is the reference. An addition (recovery rows, decide_kind) enters only if its benefit is
   established on development by its registered rule; otherwise its complexity counts against it and it is left out.
   The choice and its configuration (code commit, adapter sha256, recovery flags) are committed before test set 3 is
   opened.
3. *Recovery rows* are judged by matched seed differences: A and B side by side at seeds 7, 11 and 13, and B minus A
   within each seed, plus the step-matched B run (B's data for A's 1,971 steps) to separate the data from the extra
   steps. B at seed 11 against B at seed 7 is training-seed spread, not B's effect, and is not used as evidence on it.
4. *decide_kind* is worded as a null result unless the pooled verdict is clear of zero: four of four differences have
   been positive (+0.00 to +0.06) with every interval across zero, which by sign alone chance gives about one time in
   eight. Its 0.9 threshold is on the renormalised option-letter probability, not a calibrated probability of being
   right. Reported per arm (`experiments/screen/decide_kind_audit.json`): how often it acts (18 to 30% of
   third-party assessments), how often its changes fix a wrong label (7 to 37 per arm), how often they break a right
   one (0 to 2), and how often they swap one wrong label for another (6 to 36). Left out of the chosen configuration.
5. *Test set 3, accounting.* 48 cases × 2 attempts = 96 runs per arm (two attempts, not three, to fit three arms in
   the time left); one trained model per arm (one training seed), so the test interval covers variation between
   companies and attempts, not between training runs; uncertainty with company dependence kept (12 companies,
   t-interval over company means and a company bootstrap); attempts and seeds are not counted as independent companies.
   *Primary comparison:* the chosen fine-tuned 8B against the unfine-tuned 8B on the same scaffold. *Secondary:*
   against the Stage 1 system; development shows +0.14 to +0.31, and with 12 companies the test reliably detects only
   gaps of about 0.3, so this comparison may well be inconclusive, and the paper says so before the run.
6. *Claims.* "Fine-tuning on the teacher's trajectories improves investigation quality" is the supported result.
   "The gain comes from learning the teacher's procedure" is an explanation the comparisons do not isolate
   (distillation changes tool use, wording and evidence selection together); the paper presents it as such.
7. *Teacher comparison (Qwen against Command A+)*, if run: on identical student states, judged blind on evidence links,
   whether a proposed experiment discriminates between theories, and whether a decline is justified; a higher
   acceptance rate by the tools is not the criterion.
8. *Cut order, harder:* with the cluster full, the Qwen teacher batch and the trained decision head are cut first
   (post-deadline work; neither can reach three seeds). The Qwen batch is cancelled now (its job file stays); the
   decision head runs only if a GPU is idle with nothing registered waiting.

**Registered (14:12; before A at seed 11, either seed 13 or the step-matched run is judged, and before any
AuditKIT tool-call metric of the retrospective audit is read — job 779753 printed only replay-mismatch counts, all 0).**
*B's admission, in numbers.* B (A's data plus the 401 recovery rows) replaces A for test set 3 only if all of:
(a) B minus A (judged quality, development, guards arms, same cases, paired by run) is positive at each of seeds 7, 11
and 13; (b) the mean of the three per-seed differences is at least +0.15; (c) the pooled 95% interval (bootstrap over
cases, pairing kept within seeds) has its lower bound above 0; (d) the step-matched run (B's data for A's 1,971 steps,
seed 7) minus A at seed 7 is at least +0.09, half of B's seed-7 gain, so the gain is not the extra steps; (e) B
finishes at least as many runs as A summed over the three seeds. Otherwise A. Signs alone are not enough.
*Which adapter represents the chosen configuration on test set 3:* its training-seed-7 adapter, fixed now (seed 7 is
the reference seed every design step used); not the best development seed, which would add a selection step. Disclosed
in the paper.
*AuditKIT, mandatory.* Every evaluation job checks at its start that AgentTune and AuditKIT import, and the runner
(--require-auditkit) refuses to start without them; both are verified on both accounts before Monday's run. The 11
retrospective audits keep the original reports untouched and go to separate files beside them, with the input report's
sha256, the AgentTune and AuditKIT versions and the code revision, and are described as retrospective audits of saved
trajectories (a replay of the recorded tool calls; no model call is made).
*AuditKIT's numbers in the paper.* Where AuditKIT measures the same thing as a harness count (repeated or redundant
calls, looping), AuditKIT's number is the one reported, and any difference from the harness count, with both
definitions and denominators, is reported in the appendix. Counts AuditKIT does not compute (runs finished, guard
refusals by kind, simulated results cited as evidence) stay harness counts and are named as such.
*Checks done:* Stage 1 is unaffected (all 152 earlier reports with an AuditKIT section were audited during the run;
none logged a skip). Training used AgentTune: the trainer imports AgentTune's distillation trainer unconditionally
(src/aemon/training/train.py), so no training job could have run without it; on Nour's account training ran in
env_unsloth (AgentTune 1.1.3).
*Decision model, wording:* it improves the labels it changes (fixing 7 to 37 per arm, breaking at most 2) without
changing judged quality; either the evidence-type label matters less to the recommendation than expected, or the judge
does not register it; the paper says both are possible.

**Registered (14:26, before any hand score): a blind hand check of the judge** (pasted suggestion, adopted;
Hatem scores). 30 development packets, seeded (20), stratified: A seed 7 (8), B seed 7 (8), B seed 11 (7), version 1's
final system (7); the prompted 8B is left out because none of its packets has both dimensions scored (it rarely
reaches a recommendation). Shown as H01 to H30 in `experiments/judge_check/hand_check.html`, scored on the judge's own
rubric rows for evidence judgement and recommendation (0 to 3, or not applicable); the key mapping labels to arms is
kept outside the repository (`~/lexsi-backup/judge_keys/hand_check_key.json`). Reported per dimension: exact
agreement, agreement within one point, Spearman correlation and the level difference (judge minus hand), overall and
by arm (`scripts/judge_check/agreement.py`). One scorer, 30 packets: a check on the judge, not a human benchmark.
Also added to the paper today (no new runs): the effect at two model sizes (Stage 1 test and Stage 2 development,
reported side by side, not pooled), per-seed fine-tuning gains, an over-caution column (no arm declines a test or ends
"insufficient evidence"; every fine-tuned arm proposes a test on all 6 runs of the two cases labelled as not
warranting one), test set 3's freeze commit and hash with the nearest training or development record (character n-gram
TF-IDF cosine 0.44, generic company-size sentences), the checkpoint rule, three evaluation lessons, and toolkit and
reproduction appendices. Not run: an in-context control (the prompted 8B shown one teacher investigation); a full
investigation does not fit its 8,192-token context alongside the case, so it would need a truncated example and would
not answer the question cleanly.

**Registered (14:31, before any code or result): RL from adapter A, exploratory (Hatem: "Build and run it").**
Not eligible for test set 3 (one seed, after the Sunday cutoff); cut first if GPUs stay scarce. *Method:* GRPO through
AgentTune's Unsloth agentic GRPO wrapper (TRL 1.15), continuing A's LoRA (A's seed-7 adapter weights loaded into a LoRA
of the same rank, alpha, dropout and targets; bf16 base). *States:* single decision points replayed exactly
(`aemon.teacher.corrections._replay`) from the student run on training companies only (aya-expanse-8b-s7-student, no
guards): the 148 loop-start states of the recovery round plus other turns sampled from the same runs, so it learns
ordinary steps as well as escapes. No validation, development or test company. *Generation:* 4 sampled next calls per
state (temperature 1.0), completion at most 320 tokens. *Reward, checked by the tools, no LLM judge:* the state is
replayed and the sampled call executed in the guarded tools: −1 if it is not a parseable tool call or repeats an
earlier call; −1 if the tools refuse it as a quote not in the source or a simulated result cited as evidence; −0.5 for
any other refusal; +0.5 if accepted; +0.5 more if it makes progress (opens the next stage, or reads, assesses, adds or
revises something new). Range −1 to +1. It rewards working, non-repeating, grounded calls, not persuasive text; it
cannot see whether a call is wise, which is stated as its limit. *Training:* a fixed number of steps registered with
the job (no checkpoint selection), KL coefficient 0.04, seed 7. *Comparison:* A+RL against A at seed 7, development
guards arm, same scaffold, blind judge, plus the harness counts (finished, refused calls by kind) and AuditKIT.
A higher training reward shows only that it learned the reward; the development comparison is the evidence.

**Amended (14:31, before any code or result): the reward is validated before any training with it** (pasted
review, adopted). Order: build the reward; validate it; only then the first rung of the ladder, rejection sampling
(keep the best of several sampled next calls per state by the reward, then supervised fine-tuning on them, through
the existing AgentTune trainer); DPO and GRPO only if that rung moves development quality. *Validation, both required:*
(1) gaming probes: hand-built calls that should score badly (a repeated call, a quote not in its source, a simulated
result cited as evidence, a finish on thin evidence, a call that names nothing in the state, an unparseable reply)
each score below the student's recorded accepted call at the same state; (2) agreement: over the already judged
development runs, the run's mean step reward rank-correlates with the judge's score (Spearman at least 0.3, run
level); the judge is used only to validate the reward, never inside it. If either fails, the reward is fixed or the RL
branch stops. *Stated limit:* every term is a process check (valid, non-repeating, grounded, progressing); none sees
whether a judgement is right, so this RL can at most improve mechanical reliability, not the judgement where the
teacher is the ceiling. *Not before the deadline, written up as the next step:* an outcome reward (the agent ends with
a probability that the move succeeds, scored by Brier score against what happened, on many historical cases built
from dated public filings, with more question types), starting by measuring how calibrated the current student
already is; and the bar for any RL claim, SFT from a better teacher.

**RL branch stopped before any training (14:35): the reward failed its registered validation** (independent
review adopted). *Probes:* five of six probe types scored below the student's good call at every state built (171 states);
the sixth, a simulated result cited as support, could not be built at any sampled state and is untested, not passed
(the script now says so). *Agreement:* run-level Spearman between mean step reward and the judge's score over 855
judged development runs, 19 arms: **0.26**, below the registered 0.30, so by the rule no training. *Diagnostics only,
not used to rescue the rule:* 424 of the 855 runs replay differently from the calls actually executed (guards and the
decision model replace or redraw calls), and on the 431 faithful replays agreement is 0.16; within arms it ranges from
−0.37 to +0.55, positive for unfine-tuned models where loops sink quality (Qwen 9B +0.52, Gemma 12B +0.54, Tiny Aya
+0.22) and at or below zero for our best fine-tuned agents (A seed 7 −0.10, B seed 7 −0.36). Reading: a tool-checked
process reward measures mechanical reliability, which separates weak agents from usable ones but not good runs from
better ones once an agent stops failing mechanically; RL on it would push the fine-tuned agents along a direction
unrelated, or opposed, to judged quality. *Next, after the deadline:* a reward that sees judgement (the outcome reward
registered at 14:5x), validated under a rule frozen before fitting (a company split, fresh judgments), and compared
against SFT from a better teacher. The step reward and its validation stay in the repository
(`src/aemon/rl/reward.py`, `scripts/rl/validate_reward.py`, `experiments/rl/reward_validation.json`).

**Correction (14:37).** The entries of 13:5x and 14:0x said four positive decide_kind differences out of four
is what chance gives "about one time in eight". Four positive signs by chance alone has probability 1/16; four signs
that agree (all positive or all negative) has probability 1/8. The paper now states both. The decision model stays
worded as no detected effect on quality and stays out of the tested configuration; nothing else changes.

**decide_kind on A without the correction rows, judged (14:58).** Job 778242, decide arm (AuditKIT ran in-job):
40 of 45 finished (37 without), 72 refused calls (85); quality 2.06 against 2.02, **+0.04 [−0.04, +0.10]**, evidence
judgement 1.67 against 1.49. Five comparisons now (+0.03, +0.005, +0.06, +0.03, +0.04), all positive, every interval
across zero. Five agreeing signs by chance has probability 2·2^−5 = 1/16. Under the registered wording it stays "no
detected effect on overall quality", out of the tested configuration; the pooled three-seed verdict still waits for A
at seed 11 and both seed-13 runs.

**Scheduling (15:54).** The waiting jobs were blocked by CPUs, not GPUs: the student nodes had idle GPU slices
(gnode02 3 of 7 in use, gnode03 5 of 8) but almost no free cores (24 of 24, 30 of 32), and screens asked for 4. Screens
need few cores (the model runs on the GPU), so the waiting replication screens were lowered to 2 CPUs (A seed 11
started at once, job 779526) and 2 is now the screen default. No result is affected.

**A at training seed 11, guards, judged (17:41); B's admission decided.** Job 779526 (decide arm still
running): 41 of 45 finished, 80 refused calls (65 repeats, 13 simulated results cited). Blind quality **2.15**. Matched
seed: **B minus A at seed 11 = −0.18 [−0.34, −0.05]** (B 1.97), lower at four of six companies. Under the registered
rule (14:2x) B must beat A at each of seeds 7, 11 and 13; it does not at seed 11, with an interval below zero, so **B
is not admitted, whatever seed 13 shows: the configuration for test set 3 is A** (its seed-7 adapter, without
decide_kind), provided A has judged development results at three seeds by Sunday 23:59 (A seed 13's screen is queued).
B's seed-13 screen and the step-matched run still run and are reported, as registered, but no longer bear on the
choice. Also at seed 11: A against the prompted 8B on the same scaffold **+0.86 [+0.73, +0.99]**, all six companies
(seed 7: +0.73); against version 1's final system +0.27 [+0.16, +0.39]; A seed 11 against A seed 7 +0.14 [+0.04,
+0.25], the size of the seed-to-seed spread. The recovery rows' +0.18 at seed 7 is therefore not a reliable effect:
at the next seed the same rows cost 0.18.

**Registered (18:28, Hatem: "close this gap"; before A seed 13's screen has started, so before any of its
results): what happens if the eligibility condition is not met.** The rule of 14:05 (point 1) admits only
configurations with judged development results at three training seeds by Sunday 22 November 23:59; A has two (7, 11),
its seed-13 screen is queued. The cases, fixed now:
1. *A seed 13 is judged by the cutoff.* A meets the condition and is the configuration tested, as the rules of 14:05 and
   14:12 already give. No performance threshold for A's seed 13 was registered, and none is added now: its result is
   reported whatever it is, beside seeds 7 and 11.
2. *A seed 13's screen fails for a technical reason.* It is resubmitted at once (on whichever account has a free slot),
   as with every failed job; the cutoff still applies.
3. *A seed 13 is not judged by the cutoff* (queue, cluster or technical delay). A is still the configuration tested,
   because it is the registered reference (14:05, point 2) and the only candidate left (B fails 14:12 (a)); the paper
   states that A's development evidence covers two training seeds, not three, and that the eligibility condition was
   not met in time.
4. In every case the tested adapter is A's seed-7 adapter without decide_kind (14:12), committed with its sha256 before
   test set 3 is opened, and the final choice is Hatem's confirmation of this rule on Monday by noon, not a new choice.
No other configuration can enter through any of these cases.

**Blind hand check of the judge, scored by Hatem (18:36; design registered 14:26).** 30 development packets
(A seed 7: 8, B seed 7: 8, B seed 11: 7, version 1's final system: 7), all 30 scored on both dimensions with a note.
Agreement with codexsol170 (`experiments/judge_check/agreement.json`): *evidence judgement* exact 30%, within one
point 100%, Spearman 0.17, hand mean 1.90 against judge 1.20; *recommendation* exact 13%, within one point 57%,
Spearman −0.20, hand 2.77 against judge 1.53. Both raters bunch their scores (hand: evidence judgement 2 in 27 of 30,
recommendation 3 in 24 of 30; judge: evidence judgement 1 in 24 of 30), so the rank correlations carry little
information. Reading: the notes and the judge's reasons name the same flaws (mislabelled studies, unchecked date
cut-offs, reversal conditions resting on weak surveys); the hand scorer applied the rubric's wording literally (a next
action plus a reversal condition earns 3), the judge also docks when the reversal condition is weakly founded. So the
two disagree on level, as our two LLM judges did, and neither separates the four similar arms (hand arm means 1.75 to
2.00 and 2.71 to 2.88). This supports reading only differences, and not small ones, between similar agents. It does
not test the main effect: the prompted 8B was not sampled (it rarely reaches a recommendation), so fine-tuned against
prompted rests on the judge and the harness counts (39 against 4 runs finished). One scorer, 30 packets: a check on
the judge, not a human benchmark.

**Registered (18:38, before any hand score; Hatem: "ok yes"): a second blind hand check, on the main gap.**
10 matched pairs (same case and attempt) of A at seed 7 and the prompted 8B on the same scaffold, seeded (21), spread
over all six companies, every packet distinct, both dimensions judged in both arms; shown as 20 shuffled packets
P01..P20 (`experiments/judge_check/hand_pairs.html`), so neither arm nor pairing is visible; scored on problem
framing and evidence judgement (the prompted model reaches both). Key outside the repository
(`~/lexsi-backup/judge_keys/hand_pairs_key.json`). Reported (`scripts/judge_check/pair_agreement.py`): per
dimension, the mean gap A minus prompted by hand and by the judge, how many pairs each rater puts A ahead, level or
behind, and how often their signs agree. The judge's scores for these packets were not looked at before the hand
scores are in. One scorer, 10 pairs: it can show whether a human sees a gap in the same direction, not its size.

**Second hand check scored by Hatem (18:49; design registered 18:3x).** 10 matched pairs, A seed 7 against the
prompted 8B on the same scaffold, 20 blind packets, both dimensions scored for all (`experiments/judge_check/pair_agreement.json`).
*Problem framing:* gap A minus prompted +0.5 by hand, +0.5 by the judge; A ahead/level/behind 5/5/0 by hand, 5/3/2 by
the judge. *Evidence judgement:* +0.9 by hand, +0.3 by the judge; 7/3/0 by hand, 3/7/0 by the judge. Pair-level sign
agreement 50% and 60% (scores bunched in a few levels, so one rater's "level" is often the other's +1). Reading: the
human sees the main gap in the same direction and at least as large as the judge, and never puts the prompted model
ahead (0 of 20 comparisons); together with the first check (similar agents not separated by either rater), the hand
checks support the large fine-tuned against prompted gap and the caution about small differences between similar
agents. One scorer, 10 pairs: direction, not size.

**Recovery round rerun (19:02; Hatem: "Rerun and retrain").** The first Command A+ correction batch (job 777948)
failed: the queue line carried a literal '$HOME' path, so no state was read; it was cancelled after about 20 minutes
on the 80 GB slice, and the 148 student states are intact. Rerun as registered on 19 November 21:30: the same states,
the same teacher and correction protocol (kept only if the tools accept the call, it repeats nothing and its
justification names something in the state that the call acts on). Then rows from the kept corrections (tagged
`correction`, traced to the manifest), A's data plus them (extra rows capped at 20% of target tokens, as for A's 51
correction rows), trained at seed 7 with A's schedule, screened on development with the guards arm. Exploratory, one
seed, not eligible for test set 3 (14:05 point 1); reported against A at seed 7, paired by run.

**Retrospective AuditKIT done (19:13, job 780733).** The 11 Stage 2 reports whose run skipped AuditKIT were
audited from their saved trajectories; each audit is a separate file beside the untouched report
(`experiments/screen/*.auditkit.json`), carrying the input report's sha256 (all 11 match the local reports that were
judged), AgentTune 1.1.3 and AuditKIT 1.1.3, and the code revision. Replay mismatches: 0 in all 11. A seed 11's
screen (job 779526) ran with the older code copy on Nour's account and also skipped it; it and any later report that
skipped it go through the same retrospective audit before the paper's AuditKIT numbers are written.

**Report rule fixed (19:19): a packet judged more than once gets the mean of its judgments.** When two arms of
the same agent produce the same run (decide_kind not intervening), they share a packet, and it was judged once per
campaign: 75 packets twice, the two judgments differing by 0.13 on average (the judge's own noise). The report kept
whichever line came last, so an arm's mean shifted slightly when a later campaign was appended (A seed 11: 2.153, then
2.177). `aemon.evaluation.judging.report` now combines all of a packet's judgments by their mean, independent of line
order; the single 'judgment' field keeps its old meaning, so Stage 1's frozen release scripts are unchanged. Every
Stage 2 comparison was recomputed (`experiments/screen/judging/recomputed/`, table.txt): all move by at most 0.02 and
no conclusion changes. Changed at two decimals: A seed 11 against the prompted 8B +0.88 [+0.75, +1.00] (was +0.86),
against version 1 +0.29 (was +0.27), against A seed 7 +0.15 (was +0.14), A seed 11's mean 2.17 (was 2.15); B minus A
at seed 11 **−0.20 [−0.36, −0.06]** (was −0.18 [−0.34, −0.05]; B's exclusion under 14:12 (a) stands); B minus A at
seed 7 +0.17 (was +0.18). The paper uses the recomputed values.
**decide_kind on A at seed 11 (job 779526, decide arm):** 39 of 45 finished (41 without), 82 refused calls (80);
quality **−0.02 [−0.12, +0.07]**, evidence judgement 1.73 against 1.58. Six comparisons now range −0.02 to +0.06, five
positive, every interval across zero: no detected effect on quality, as registered.

**Inference cost bench done (19:23, job 776913, A seed 7 merged adapter, one 4g.40gb slice).**
`experiments/bench/inference_summary.json`: 12 settings (bf16, Q8_0, Q4_K_M × 1, 4, 8, 16 investigations at once;
15 runs at 1, 45 otherwise). Best throughput Q4_K_M at 8: 93.8 investigations per GPU hour, 39 of 45 finished,
$0.0188 per investigation at the median A100 40GB price ($1.76/h, priced as a whole GPU although the slice is 4/7 of
one); bf16 at 16: 84.6/h, $0.0208; Q8_0 at 4: 73.8/h, $0.0239. Claude Haiku 5.5 measured: $0.0084 per
investigation. So, as measured and priced, the self-hosted agent costs about 2.2 times Haiku per investigation; break-even
is about $0.79 per GPU hour at the best throughput (the low aggregator price is $0.89). Quantization does not lower
the finish rate in these runs (Q8_0 finished 15 of 15 at one at a time against bf16's 12), but quality per precision was
not judged, and Haiku's quality on these cases was not judged in Stage 2: this is cost per investigation, not cost at
equal quality.

**Scheduling (19:55): A seed 13's screen moved ahead.** Its job on Hatem's account (779177) stayed pending
behind Nour's higher fair-share. A twin (780862) runs on Nour's account with the same code copy (1a8e7ab, as A's seeds
7 and 11), the same adapter (sha256 99a217e2..., checked after the copy) and settings; to give it a running slot,
ablation group 1 (779763, started a minute earlier) and guard ablation 2 (780747, pending) were cancelled, both
completeness runs, to be resubmitted; the original is cancelled once the twin's first runs are recorded. The teacher
batch keeps a lower priority than the twin. No result is affected; A seed 13's eligibility (14:05 point 1) is what
the move protects.

**Registered (20:01; Hatem: "for the final test we'll use 2 judges"; before any test set 3 run): the two
judges for test set 3 and how they combine.** Judges: `codexsol170` (gpt-6-sol, codex-cli 0.170.0) and `claudecode`
(claude-opus-5-5, effort medium, Claude Code CLI print mode on the subscription login, no API key), the pair used on
Stage 1's test set 2, each under its existing scoring qualification (`reports/judge/codexsol170_score_qualification.json`,
`reports/judge/claudecode_score_qualification.json`), the frozen judge prompt and rubric (judge-v1), one blind
shuffled packet set for all three arms, keys outside the repository until both judges finish. *Primary score of a
run:* the mean of the two judges' run scores (each the mean of its judged dimensions, unreached dimensions 0; a packet
judged more than once by one judge takes that judge's mean, as of 19:2x). Runs one judge could not score validly are
listed and left out of the primary comparison, never re-judged selectively. *Reported:* the primary comparisons
(fine-tuned A against the prompted 8B; secondary, against the Stage 1 system) with the company-level interval of 14:05,
each judge's own comparison beside it, and the judges' agreement (Spearman on runs, mean absolute difference). If the
two judges disagree in sign on the primary comparison, that is reported as such, not resolved by picking one.
*Cost:* `claudecode` runs on the subscription, so no per-token charge is expected; if it cannot run (login or usage
limits), the API backend `claude` (same model, qualified, priced) is used only after its cost estimate is shown to
Hatem and approved.

**Test set 3 tooling prepared (21:08; nothing run, test set 3 not opened).** `scripts/test3/analyze.py`
implements the registered reading (mean of the two judges, Eq. 3's company t-interval with a company bootstrap and the
case bootstrap beside it, each judge's comparison, agreement, sign disagreement flagged, unscored runs listed); run on
Stage 1's two-judge test set 2 it reproduces the published numbers (+0.518; company t [0.253, 0.782] against
[0.25, 0.78]; company bootstrap [0.294, 0.746] against [0.29, 0.75]; Spearman 0.954, mean absolute difference 0.295),
`experiments/test3/validation_on_stage1_test2.json`. `scripts/test3/preflight.sh REV` checks, read-only, both
accounts' code copy, test set 3 files against the local freeze, llama.cpp, the environments' AgentTune and AuditKIT,
A's seed-7 adapter (sha256 490d47e3d607c193..., identical on both accounts) and the Stage 1 system's files; it passes
against code copy e3a19cc. `scripts/test3/run_test3.sh REV` submits the three registered arms (48 cases × 2
attempts; the two 8B arms differ only in the adapter, as on development), waits, builds one blind packet set, runs
both judges and the analysis. Two job fixes it needed: the screen job now takes SPLIT (it always loaded development
cases), and the Stage 1 system's job (eval_switch) now checks the required tools and audits in-job. Monday needs a
fresh deploy of the code with these fixes, then the preflight against it.

**Seed 13 judged (22:48); A meets the eligibility condition; B's rule fully evaluated.**
*B seed 13* (job 779527, guards; the first judging returned nothing at Codex's usage limit and was re-judged in full
after the reset, 25 of 25 valid): 42 of 45 finished, 40 refused calls; quality **2.13**; against the prompted 8B
+0.84 [+0.67, +1.02]; against version 1 +0.26 [+0.12, +0.38]. *A seed 13* (twin job 780862, guards, 35 packets valid):
39 of 45 finished, 93 refused calls; quality **2.06**; against the prompted 8B **+0.77 [+0.69, +0.85]**, all six
companies; against version 1 +0.18 [+0.09, +0.27]; against A seed 7 +0.04 [−0.07, +0.17], against A seed 11 −0.10
[−0.23, +0.01]. **A now has judged development results at seeds 7, 11 and 13 (2.02, 2.17, 2.06), so it meets the
eligibility condition of 14:05 point 1, case 1 of 18:28.** Fine-tuning against the prompted 8B on the same scaffold:
+0.73, +0.88, +0.77, every interval above zero. *B's admission (14:12), each condition:* (a) B minus A per seed +0.17,
−0.20, +0.07: not positive at every seed, fails; (b) mean of the three +0.02, below 0.15, fails; (c) pooled +0.02
[−0.04, +0.09] (bootstrap over cases, pairing within seeds), lower bound not above 0, fails; (d) the step-matched run
is not judged yet and cannot change the outcome; (e) B finishes 128 runs against A's 119 over the three seeds, met.
B is not admitted; the test configuration is A's seed-7 adapter without decide_kind, as registered, subject to Hatem's
confirmation on Monday. Recorded for the paper: the recovery rows raise the finish rate (128 against 119) without a
reliable change in judged quality.

**Composition condition judged (23:04; exploratory, one seed, not eligible).** A's teacher rows resampled by
skill group (temperature 0.5) at A's token budget, seed 7 (job 777458; screen 779266): 17 of 45 finished, 248 refused
calls (245 repeats). Quality **1.04 against A's 2.02: −0.98 [−1.37, −0.58]**, below even the prompted 8B on the same
scaffold (−0.26 [−0.60, +0.08]); every dimension lower except problem framing (assumptions −1.69, distinct theories
−1.65, causal mechanism −1.40, revision −1.35, evidence judgement −0.97, recommendation −0.73). With decide_kind +0.03
[−0.06, +0.14]. *Checked before believing it:* training ran normally (3,996 rows, 1,998 steps, held-out loss 0.435
against A's 0.386 on the same 240 natural-mix rows); the change is the mix: revision rows 85 → 252 (the same scarce
examples about three times each), assessment 514 → 648, theories 1,153 → 909, position 338 → 278. *Reading,
registered as a hypothesis, not a finding:* up-weighting scarce skills by repetition makes the student repeat itself
(loops), so rebalancing distillation data naively can break the procedure; the teacher's natural mix is the safer
default. One seed; the paper says so.

**decide_kind decided under the rule of 19 November 20:20 (23:23).** Seed-13 decide arms judged (A: job 780862,
34 packets; B: job 779527, 28 packets). Per seed, on minus off: A +0.03, −0.02, +0.04; B +0.01, +0.06, −0.06. Pooled
over the three training seeds (bootstrap over cases, pairing within seeds): **A +0.01 [−0.03, +0.06], B +0.00 [−0.07,
+0.06]**. The rule needs the pooled interval above 0: not met for either, so decide_kind is **not shown to help** and
stays out of the tested configuration. Nine comparisons in all (three seeds of A and B, the prompted 8B, A without
corrections, composition) range from −0.06 to +0.06. As registered (14:12): it improves the labels it changes; no
detected effect on judged quality.

**Ablation, no guards (primary row), judged (23:53; job 780898, A seed 7's adapter, none arm).** 21 of 45
finished (A with guards: 39), 19 stopped on repeated errors, 263 refused calls (146). Quality **1.57 against 2.02:
−0.44 [−0.67, −0.24]**, lower at all six companies (Jotun −1.04, Tanita −1.00). Under the rule of 19 November 20:20
(a part earns its place if removing it lowers the judge score with the interval below 0, or lowers finished runs by 5
or more of 45 without a judge gain) the guards earn their place on both counts. The fine-tuned agent needs its
decoding guards: fine-tuning and guards are complements, not substitutes. Which guard groups matter: the four
guard-group arms follow.

**Step-matched B run judged (00:04; B's data for A's 1,971 steps, seed 7; job 780770, 44 packets).**
10 of 45 finished, 35 stopped at the turn limit, 305 refused calls (all repeats: 299 searches, almost all in the
theories stage, where the agent searches and reads without ever adding a theory). Quality **0.66: against A seed 7
−1.36 [−1.65, −1.00], against B seed 7 −1.53 [−1.85, −1.15]**. *Checked before believing it:* training normal (4,343
rows, held-out loss 0.392 against B seed 7's 0.390 on the same rows); the served adapter is the trained one (sha256
19f09b08...); same code, settings and template checks as every B screen. *Reading:* a behavioural failure, not an
infrastructure one; with B seed 11's loops at one company, B's data gives agents that loop unpredictably across seeds
and schedules, so its seed-7 gain was fragile. Condition (d) of B's rule (14:12) fails as well (−1.36 against the
required +0.09): B fails (a), (b), (c) and (d). Nothing changes for test set 3 (A).

**Is the gain more than finishing? (01:56; pasted review, adopted.)** Stage 1's reached-only comparison
(each pair compared only on the dimensions both runs were scored on; `scripts/paper/shared_stages.py`) on the 8B
development results, one judge: A against the prompted 8B, full **+0.73, +0.87, +0.77** at seeds 7, 11, 13; shared
stages only **+0.60 [+0.46, +0.73], +0.73 [+0.61, +0.85], +0.62 [+0.54, +0.68]** (45 of 45 pairs share stages; 7.2 to
7.3 of 9 dimensions on average). About 0.13 to 0.15 of the gain is finishing more of the procedure; the rest is
better work on the stages both reach. Against the Stage 1 system unchanged (+0.15, +0.29, +0.19).
**Registered now, before any test set 3 run: a secondary analysis for test set 3**, the same shared-stages comparison
per judge, then averaged over the two judges (as Stage 1), with the company t-interval; reported beside the primary,
never in place of it.
**Also registered (pasted review):** results that arrive after the eligibility cutoff or with one seed (the decision
head, the recovery-round retrain) go in the appendix as exploratory, whatever they score; the "two sizes" paragraph
claims only that direction and rough size agree until test set 3 gives an 8B test result to compare with the 3B one.

**Public release of Stage 2 (01:59; Hatem's choices).** Pushed to the public repository (HatemSaadallah/aemon)
only after test set 3 is run and in the paper, and after Sunday's 1:1 says whether the submission must be anonymous.
Contents: code, the paper (PDF and LaTeX), test set 3's data, all development and test reports with blind packets and
judge predictions, and both hand-check exports. Built with `scripts/release/build_public_repo.py` (no history,
identifiers replaced, working notes dropped). The Stage 2 decision log is published with the judges named (they are
the instruments) and the notes that an AI assistant reviewed a design reworded to what was checked. Nothing is pushed
before Hatem's go.

**Ablations judged overnight (02:09; A seed 7's adapter, same server, cases and attempts; exploratory rows, so
direction and size only under the rule of 19 November 20:20).** Blind, codexsol170, against A with all guards
(2.02, 39 of 45 finished); `experiments/screen/ablation_stage2_A7_partial2.json` for the mechanical table.
- `routed` (adapter off for position, update and conclude; job on Nour's account): **1.81, −0.20 [−0.30, −0.11]**,
  18 of 45 finished (−21), median 42 turns against 35. Handing the late stages back to the base model costs both
  quality and finishes: the adapter helps on the stages after the evidence too. Against the prompted 8B it is still
  +0.52 [+0.41, +0.63].
- `minus_quote` (quote_menu off): **1.96, −0.06 [−0.13, +0.01]**, 35 of 45 finished (−4); small and not clearly
  below zero.
- `minus_repeats` (resampling of repeated calls off): mechanical only so far, 13 of 45 finished (−26), 328 refused
  calls (146); its judging stopped at the judge's usage limit (16 of 43 valid, set aside) and is redone in full.
- B step-matched, decide arm (job on Hatem's account, BS7): 0.67 against its guards arm's 0.65, +0.02 [+0.00, +0.05];
  B stays out of test set 3 (its rule failed at 00:04). Late, one seed: appendix only.
Waiting: `minus_repeats` (rejudge), `minus_budget`, `minus_ledger`, `staged_prompt`, and the recovery round's screen.

**Decision head (evidence kind), offline result (02:11; job 781448, A's base with the trained LoRA and letter head,
seed 7; rule and amendment of 20 November 12:xx).** On the 121 frozen test items, after one fitted temperature per
arm: trained head **79.3%** against the zero-shot base's **81.0%** (registered as 81.8% from the earlier
measurement; 81.0% here with this run's temperature fit), paired difference **−1.7 points [−10.9, +8.1]** over 95
records (head right and base wrong on 12 items, the reverse on 14). Calibration error is lower (0.07 against 0.18).
On the 48 third-party items, the only ones decide_kind acts on: 47.9% against 52.1%. On the in-distribution
calibration split it rose from 61% to 83%, so training fitted the dossier excerpts but did not carry over to the
agent-chosen test quotes. **Go rule not met** (needs +5 points, no worse calibration and a paired lower bound above
0): reported offline only, and no in-loop run. Files: `experiments/decider/kind-s7/` (adapter sha256 in
`decider.gguf.sha256`). Exploratory; appendix only.

**General-ability retention check submitted (02:16; job 781541, Hatem's account).** The ablation plan's general-ability
row (19 November 20:30), not yet run: the base against A seed 7 (adapter sha256 490d47e3...) on version 1's sampled
MMLU and ARC-Challenge items (`reports/retention/retention_items.jsonl`, sha256 7ce21200..., identical to the
committed file), one server, `jobs/retention_aya.sbatch` at e3a19cc. Mechanical scoring, no judge. Reported as
measured; a drop is described, not tested against a threshold (none was registered).

**Quantity condition: data and settings, registered before any of it runs (02:23; Hatem: "do both").** The 19
November 23:43 entry's quantity condition, made concrete. *New training companies:* the 35 `train3` companies (70
cases, base and irrelevant what-if; dossiers verified word for word, commit e0834c1, 10 November) are already in the
training split, and none of them is in A's rows (A's 4,302 rows cover the 63 version 1 companies), so no new research
is needed. *Collection, the same way as version 1's:* Command A+ Q4_K_M (weights a26ba92), prompt `teacher`,
teacher-v2, reasoning budget 512, 4 slots, context 16,384 per slot, temperature 0, one attempt per case (first attempt
1), batches of two companies, the stage check after each batch; code e3a19cc; queue `qtyh*` on Hatem's account and
`qtyn*` on Nour's (the second after the recovery batch frees its 80 GB slice). *Rows:* `aemon.rows.build_rows
--compact --prompt compact` as version 1's (job 744559), from the accepted reports only; appended to A's rows and
corrections; trained at seed 7 with A's recipe (2 epochs, so more steps: steps and supervised tokens reported).
*Reading:* the development screen (guards), one judge, against A seed 7; exploratory and late, so appendix only, and
never sent to test set 3. If collection is not done by Sunday 22:00, the rows from the batches finished by then are
used and the shortfall is reported.

**Retention, measured (02:27; job 781541).** Zero-shot, letter by log-probability, 800 items (version 1's sample):
A seed 7 **67.9%** against the Aya Expanse 8B base's **67.3%**, adapter minus base **+0.6 points [−0.6, +1.9]**
(ARC-Challenge 81.0% against 81.3%, −0.3 [−2.7, +1.7]; MMLU 60.0% against 58.8%, +1.2 [−0.4, +2.8]). Fine-tuning for
the investigation did not lower general multiple-choice ability on this sample. Files: `experiments/retention/`.

**Recovery round, why it stopped and how it is completed (02:27).** The 1-slot retry (job 780714) answered 67 of
the 148 states (23 kept) before its llama.cpp server aborted on a CUDA error ("invalid argument", the mismatch between
the binary and the GPU it runs on that version 1 met; fixed then by rebuilding on the node, `REBUILD=1`, which this
job lacked). The other 81 requests failed to connect. The 81 are re-asked with the same settings as the 67 (reasoning
budget 1,024, teacher-v1, the job's defaults), 4 slots and a server rebuilt for the GPU (job 781576, Nour's account);
the driver (`recovery_round_rerun2_21nov.sh`) then builds rows from both halves, trains at seed 7 and screens, as
registered. The quantity collection on Nour's account (781577) starts after it.

**Paper numbers checked mechanically (02:33).** `scripts/paper/check_numbers.py` recomputes the 14 development
comparisons the paper reports from the combined key and predictions and checks each printed difference and interval.
On the merged files of 02:20 (`stage2t_all`), 7 match and 7 differ by 0.01 to 0.02 from the printed values (for
example A against the prompted 8B at seed 7: +0.72 [+0.59, +0.86] against the printed +0.73 [+0.60, +0.85]); on the
earlier merge (`stage2s_all`) they match. Cause: later campaigns judged packets identical to earlier ones (a run
can be byte-identical across arms), and under the 19 November 19:19 rule a packet takes the mean of all its
judgments, so values shift as judgments accrue. No conclusion changes. The printed values are refreshed from the final
merge once development judging ends, and the check must then pass with no mismatch. Title changed (Hatem): "Weights and
Harness Are Complements: Distilling a Scientific Strategy Investigator into an 8B Model".

**Correction (02:36).** Seven entries of this night carried times I estimated instead of reading the clock (02:20,
02:35, 02:25, 02:55, 03:05 twice, 03:50); each is now its commit time (02:09, 02:11, 02:16, 02:23, 02:27 twice,
02:33). The order of events is unchanged: the quantity condition was registered (commit 0c8578e, 02:23) before its
teacher jobs were submitted.

**Recovery round: the re-ask failed too, and why (03:55).** Job 781576 (Nour's account) asked the 81 states and got
no answer: its `REBUILD=1` step needs cmake, which exists only in Hatem's tools folder, so it fell back to the old
binary, whose server aborted at once on this GPU (CUDA "invalid argument"), at 4 slots and again at 1. The driver
then started training on the first half's 23 rows alone (job 781681); I cancelled it before it ran and stopped the
driver, since that is not the registered round. Fix: the server binary built for compute capability 8.0 on Hatem's
account (version 1's collection binary, sha256 3477b1ee...) is copied to Nour's account at the path the job checks, in
time for the quantity job there (781577); and the 81 states are re-asked on Hatem's account (job 781694, same
settings as the first 67: reasoning budget 1,024, teacher-v1, 4 slots), ahead of Hatem's quantity job (781567 now
waits for it). The new driver (`recovery_round_rerun3_21nov.sh`) refuses to train unless at least 60 of the 81 are
answered. `minus_repeats`' existing packets are judged in full by a helper, since the queue will not rebuild packets.

**Ablation `minus_repeats` judged (03:58; exploratory row, direction and size only).** A seed 7, with refusal of
repeated calls in place of resampling them (no_repeats instead of resample_repeats); its packets were judged in full
by a helper (43 valid), since the queue does not rebuild packets that exist. Quality **1.51 against A's 2.02: −0.50
[−0.72, −0.32]**; 13 of 45 finished (39), 328 refused calls (146), most runs stopping on repeated errors. Against
the prompted 8B with the same scaffold it is +0.22 [−0.03, +0.45]. Of the guard groups measured so far, resampling a
repeated call instead of refusing it carries most of the guards' value: refusing alone leaves a fine-tuned agent that
repeats itself until it is stopped. Merged files: `stage2u_all`.

**Ablation `minus_budget` judged (04:00; exploratory row).** 41 judgments valid at first and 4 judge calls that
timed out (TimeoutExpired, not verdicts); the queue set the result aside and could not retry it, so the 4 timed-out
results were moved to `judge_results/timeouts/` (kept) and the campaign resumed, which reuses the 41 and judged the 4
again (all valid; the instrument's resume path, which refuses a changed packet or instrument). Quality **2.02 against
A's 2.01: +0.01 [−0.00, +0.04]**; 39 of 45 finished in both, 148 refused calls (146): with the budget guard off the
agent behaves almost identically, so on these cases the budget guard rarely acts. (A's mean reads 2.01 here, 2.02
before: one more repeated judgment of an A packet, averaged as registered.) Merged files: `stage2v_all`.

**Recovery first on the one 80 GB slice we hold (04:10).** The cluster has two 80 GB slices; the other has been held
by another user for 21 hours with more jobs queued above ours, so the re-ask on Hatem's account (781694) could have
waited a day. The recovery round was registered before the quantity condition and its result is pending in the
paper, so it goes first: Nour's quantity job (781577, 15 minutes into its first batch) was cancelled, that batch put
back at the front of its queue (its partial files kept in `quantity/cancelled_qtyn0/`), and the 81 states re-asked on
Nour's slice (job 781736, same settings as the first 67, the GPU-built binary); Nour's quantity collection follows it
(781737) and Hatem's (781567) waits for a slice on its own. A slip on the way: freeing the slice let Hatem's re-ask
(781694) start on it within seconds, and my next command cancelled that job; Nour's job then took the slice, so
nothing was lost but a minute. Drivers updated: `recovery_round_rerun4_21nov.sh` (job 781736) and the quantity driver
(jobs 781567, 781737).

**Ablations complete (04:15; A seed 7, development, one judge; `experiments/screen/ablation_stage2_A7_full.json`).**
Against A with all guards (2.01 on the latest merge, `stage2w_all`; 39 of 45 finished, 146 refused calls):

| Arm (one change) | Quality vs A | Finished | Refused | Median turns |
|---|---|---|---|---|
| none (no guards; primary row) | −0.44 [−0.67, −0.24] | 21 | 263 | 28 |
| minus_repeats (refuse repeats, no resampling) | −0.50 [−0.72, −0.32] | 13 | 328 | 31 |
| routed (base model for position, update, conclude) | −0.20 [−0.30, −0.11] | 18 | 197 | 42 |
| staged_prompt (Stage 1's staged prompt, not compact) | −0.20 [−0.32, −0.07] | 26 | 62 | 17 |
| minus_quote (quote menu off) | −0.06 [−0.13, +0.01] | 35 | 162 | 35 |
| minus_ledger (grounded-beliefs ledger off) | −0.01 [−0.07, +0.04] | 40 | 133 | 35 |
| minus_budget (budget guard off) | +0.01 [−0.00, +0.04] | 39 | 148 | 35 |

Reading (exploratory rows, direction and size only; the primary row passed its rule at 23:53): of the guards, resampling
a repeated call carries nearly all the value; the ledger and budget guards rarely act on these cases; the quote menu is
small. The adapter matters in the late stages, and the prompt format it was trained in matters (the staged prompt's
runs are short and stop early: median 17 turns, 21 distinct runs among 45). `staged_prompt` has 21 packets for 45 runs
because many of its runs were byte-identical; every run maps to a judged packet.

**Recovery round: teacher half complete (06:31; job 781736).** The 81 re-asked states: all answered (0 request
failures, 4 slots, the GPU-built binary), 17 kept by the correction checks; the most common rejection, as in the first
half, is a justification that names nothing from the state (25). With the first half's 23 kept of 67 answered, the
round has 40 kept corrections from 148 states (27%). The driver now builds rows from both halves, trains A's data plus
them at seed 7 (A's schedule, extra rows capped at 20% of target tokens) and screens the guards arm, as registered.
Both quantity collections are running: Hatem's account on gnode04 (server up at 06:28, 4 slots; the binary restriction
recorded for gnode04 on 4 November no longer applies) and Nour's on gnode02 (from 06:30).

**Teacher job ends FAILED on an empty queue: a script bug, fixed (06:40).** Job 781736 finished its stage (81 answered,
written at 06:30) and then exited 1: in queue mode `take()` returns the status of its last test, which is 1 when the
queue is empty, and under `set -e` the caller's `LINE=$(take)` stopped the job before "queue empty". The data are
complete; only the job state is wrong. The recovery driver required COMPLETED and stopped; it now continues when the
re-ask's output exists (`recovery_round_rerun5_21nov.sh`). `jobs/command_a_plus.sbatch` returns 0 on an empty queue
(checked in a shell with `set -euo pipefail`); the running quantity jobs use their own copy, and the quantity driver
waits on their queue state, not their exit state.

**Composition at training seed 11, judged (08:15; job 781992; the 19 November 23:43 rule adds seeds 11 and 13 to a
condition that differs from the reference).** Same rows (composition_s7.jsonl) and recipe as seed 7: 21 of 45
finished, 21 stopped at the turn limit, 3 on repeated errors, 33 refused calls; 21 packets for 45 runs (identical runs
share a packet). Quality **1.07 against A seed 11's 2.17: −1.09 [−1.47, −0.71]**; against the prompted 8B on the same
scaffold −0.22 [−0.53, +0.11]. Seed 7 on the same merge: −0.97 [−1.36, −0.57]. The failure replicates at a second
training seed; at seed 11 the runs stall to the turn limit rather than being refused for repeats, both forms of not
moving forward. Seed 13's screen waits for a slot. Merged files: `stage2x_all`.

**Composition seed 13's screen moved to Hatem's account (08:24).** It waited for a slot on Nour's account (782011, held
by the recovery training until about 11:40) while Hatem's had one free. The adapter was copied and its sha256 checked
(40d42c52..., as trained), 782011 cancelled before it started, and the same screen (code e3a19cc, compact prompt,
guards, context 8,192) submitted on Hatem's account as job 782086. Its report is copied to Nour's account when it
lands, where the judge queue looks for it.

**A confirmed for test set 3 (Hatem, 08:55 Saturday: "confirm A").** Checked against every registered condition
before recording, none still open that could change it: (1) eligibility (three judged seeds by Sunday 23:59): A has
them (2.02, 2.17, 2.06); the recovery retrain, the quantity run and the decision head have one seed and cannot be
chosen; (2) choice: A is the reference and an addition enters only with its benefit established by its rule; B failed
its admission rule (pooled +0.02 [−0.04, +0.09], step-matched 0.66); decide_kind showed no benefit pooled over three
seeds (A +0.01 [−0.03, +0.06]); composition, which may reach three judged seeds this morning, is −0.97 and −1.09 at
the two judged seeds, so no seed-13 result can establish a benefit. Configuration: A's seed-7 adapter (sha256
490d47e3d607c193...), compact prompt, the six guards, no decide_kind, adapter on every stage (route default=0),
context 8,192, Aya Expanse 8B at 5062468b. The code revision is frozen at Monday's deploy, after preflight, and
committed with this configuration before test set 3 is opened.

**Quantity collection: Nour's job stopped, its batches moved (09:12).** Job 781737 collected its first batch (qtyn0,
4 investigations, 4 slots), but the stage check after it crashed: Nour's teacher environment (`~/lexsi/env`) has no
AgentTune, and the check imports the row builder, which imports the audit module, which needs it. The job retried the
batch at 1 slot (same crash) and stopped; another user's job then took the 80 GB slice. The investigations themselves
are unaffected (the check only reads them). Fix: Nour's 8 remaining batches are appended to Hatem's queue, where job
781567 (gnode04, an environment with AgentTune 1.1.3 at d4db4c1) takes them after its own, same settings, about one
hour a batch, so collection ends near midnight, inside Sunday 22:00. The 1-slot duplicate of qtyn0 is set aside
(`quantity/duplicate_retry/`); qtyn0's 4-slot report is used. The driver now waits on 781567 only, takes each batch's
first report (its retry only if the first is missing), and builds rows with Nour's `env_train` (same AgentTune build),
not `env`, which would fail the same way. Rows still pass build_rows' replay and provenance checks before any training.

**Composition at training seed 13, judged; composition over three seeds (09:58).** Job 782086 (moved to Hatem's
account): 36 of 45 finished, 8 stopped on repeated errors, 1 at the context limit, 130 refused calls; 37 packets.
Quality **1.98 against A seed 13's 2.06: −0.08 [−0.17, +0.01]**, +0.69 [+0.57, +0.80] over the prompted 8B. Unlike
seeds 7 (−0.97, 17 finished) and 11 (−1.09, 21 finished), it does not collapse. Pooled over the three seeds as
registered (pairs within seed, bootstrap over cases; `scripts/paper/pooled_seeds.py`, which reproduces B's recorded
+0.02 [−0.04, +0.09] exactly): **−0.72 [−0.92, −0.50]**, below A at every seed. Reading, corrected: rebalancing the
teacher's data toward rare skills does not break the agent every time; it makes it fragile, collapsing into repeats or
stalls at two of three training seeds and nearly matching A at the third, the same instability across seeds seen with
B's recovery rows. Composition is not a candidate for test set 3 (A was confirmed at 08:55; it is below A at every
seed). Merged files: `stage2y_all`.

**Recovery round trained (11:30; job 781960, Nour's account).** A's rows plus 91 extra rows (A's 51 corrections and
the round's 40), seed 7, A's recipe: 3,982 rows, 1,991 steps (A: 1,971), 4.3 hours, peak 19.7 GB; held-out loss
0.572 at step 50 and 0.387 at the end (A: 0.565 to 0.387, the same 240 validation rows). Adapter sha256
de11b0965687ab7d... The guards screen (job 782414, compact prompt, same code and settings as A's screens) is queued;
the judge queue takes it as `ayaR7_guards`. One seed, late: appendix only, compared with A seed 7.

**Recovery round judged (13:10; job 782414; one seed, late: appendix only, exploratory).** A's data plus the 40
teacher corrections of the student's own failure states (and A's 51), seed 7: 36 of 45 finished (A: 39), 8 stopped
on repeated errors, 72 refused calls (146), median 28 turns (35); 36 packets. Quality **2.12 against A seed 7's 2.01:
+0.12 [+0.02, +0.21]**, higher at 5 of 6 companies (Hellberg −0.06); by dimension, causal mechanism 2.91 against
2.57, problem framing 2.71 against 2.33, recommendation 1.36 against 1.17, experiment design 1.31 against 1.16,
revision 2.15 against 2.31, the rest within ±0.11. Against the prompted 8B +0.83 [+0.73, +0.92]; against the Stage 1
system +0.24 [+0.15, +0.33]; against B seed 7 −0.07 [−0.19, +0.07]. Caution, registered before reading it (the 21
November late-runs rule): one training seed, and B's recovery rows also gained at seed 7 (+0.17) and did not replicate
(pooled +0.02), so this is a direction worth a three-seed test, not a finding. It cannot change test set 3 (A is
confirmed; one seed is not eligible). Merged files: `stage2z_all`.

**Recovery round at seeds 11 and 13, registered before they run (13:20).** The 19 November 23:43 rule adds training
seeds 11 and 13 to any condition that differs from the reference; the recovery round does at seed 7 (+0.12 [+0.02,
+0.21]). Same rows (`rows/final.jsonl` b963e777..., extras `extras_round1.jsonl` c0913c5b..., 91 rows, identical on
both accounts) and recipe as seed 7 (job 781960, code 90dde44, Unsloth, extras capped at 20%); seed 11 on Hatem's
account, seed 13 on Nour's; then the guards screen of each (code e3a19cc, compact prompt) and the judge, as for every
seed. Reading, fixed now: the three seeds pooled as registered (pairs within seed, bootstrap over cases,
`scripts/paper/pooled_seeds.py`) against A at matched seeds; reported in the appendix with direction and size, the
paper's wording following the pooled interval; A remains the configuration for test set 3 whatever the result.

**Quantity collection: a batch failed its check; collection continues (14:05).** Job 781567 finished 7 batches (each
4 of 4 investigations finished, about 95 candidate rows a batch); batch qtyh6 then finished only 1 of 4 (3 stopped on
repeated errors) and failed the stage check, which stops the job by design, as version 1's teacher stopped on batch
again7. Its report stays; build_rows keeps only accepted investigations. The driver took the job's end for the end of
collection and built rows from 8 of 18 batches (job 782787); no training was started, and those files are set aside
(`rows/partial_quantity_1358/`). The driver now ends collection only when the queue is empty or at the registered
Sunday 22:00 cutoff, and resubmits a stopped teacher job with the same settings: job 782791 (Hatem's account) is first
in line for the next free 80 GB slice; both are held by other users' jobs, so the 10 remaining batches may not all
finish by the cutoff, in which case the finished ones are used and the shortfall reported, as registered.

**Recovery round over three seeds, judged (19:45; read as registered at 13:20).** Seeds 11 (job 783203, 33 packets)
and 13 (job 783182, 37 packets), same rows and recipe as seed 7. Against A at the matched seed: seed 7 **+0.12
[+0.02, +0.21]**, seed 11 **−0.05 [−0.15, +0.05]** (2.11 against 2.17; 40 finished, 41), seed 13 **−0.14 [−0.29,
−0.01]** (1.92 against 2.06; 41 finished, 39; 200 refused calls against 93). Pooled over the three seeds (pairs within
seed, bootstrap over cases; `scripts/paper/pooled_seeds.py`): **−0.03 [−0.07, +0.02]**. The seed-7 gain does not
replicate: one round of teacher corrections on the student's own failure states shows no reliable effect on judged
quality, the same pattern as B's rule-built recovery rows (+0.17 at seed 7, pooled +0.02). Against the prompted 8B every
seed stays far ahead (+0.83, +0.82, +0.63). Appendix only; A remains the configuration for test set 3. Mechanical table:
`experiments/screen/recovery_round_three_seeds.json`. Merged files: `stage2aa_all`.

**Quantity condition: collection stops at 14 of 18 batches (Hatem, 19:55: "let's just finish 14 batches instead of
18"), decided before any quantity result exists.** Batches done or running: Hatem's qtyh0 to qtyh8 (qtyh6 failed its
teacher check, 1 of 4 finished), Nour's qtyn0, and qtyn1 to qtyn4 on Hatem's account: 14 batches, 28 companies of the
35, 56 cases. The 4 unstarted batches (qtyn5 to qtyn8: Sartorius, Terumo, Valmont, Yaskawa) are set aside in
`quantity/dropped_hatem_1955`, never collected. The condition is otherwise unchanged: rows from the accepted
investigations only, appended to A's data, trained at seed 7, screened and judged against A seed 7; appendix only. The
paper reports how many investigations were added (accepted, and as a share of A's 205).

**Paper numbers refreshed from the latest merge (20:30; `stage2aa_all`, all development judging except the quantity
arm).** `scripts/paper/refresh_numbers.py` finds each printed comparison by recomputing it on earlier merges and
replaces it with its value on the latest; the rest (two values split across a line, the per-seed means and gains
printed without intervals, the shared-stages and staged-prompt comparisons, Figure 1's caption) were updated by hand
from recomputed values. Changes are 0.01 or 0.02 and no conclusion moves: for example A against the prompted 8B at seed
7 is +0.72 [+0.59, +0.85] (was +0.73), shared stages at seed 7 +0.59 [+0.45, +0.72] (was +0.60), no guards −0.43
[−0.66, −0.23] (was −0.44), A's seed-7 mean 2.01 (was 2.02). `scripts/paper/check_numbers.py` now passes: all 13
interval comparisons it checks are printed as the latest merge gives them (step-matched B is printed as a mean only,
so it left the interval check). `fig_seeds.pdf` regenerated from the same merge. Rerun both after the quantity arm,
since its judgments could add to shared packets.

**Quantity collection complete; driver restarted after a network drop (21:50).** All 14 batches finished (the last,
qtyn4, at 20:52; Hatem's account holds 13 reports, Nour's qtyn0). Job 782791 ended FAILED only through the
empty-queue bug of its older script copy (fixed at f043cac). Around 21:10 the laptop lost its connection to the cluster;
the driver read the unanswered queue query as empty and stopped when copying failed, with nothing done on the cluster.
It now retries on an unreadable answer, and was restarted: copy the reports, build rows (build_rows --compact --prompt
compact, Nour's env_train), append to A's rows, train at seed 7, screen.

**Quantity: rows, training and screen moved to Hatem's account (22:50).** Copying the 13 reports through the laptop
failed when the link dropped again (report qtyh1). Hatem's account already holds those 13 reports, A's rows (same
sha256 b963e777...) and an environment with AgentTune, so only Nour's qtyn0 report and its provenance lines are copied
over; rows, training at seed 7 and the screen run there (`quantity_after_21nov.sh`, every remote command retried).
Nothing else changes. The laptop was low on memory at the time (1.6 GB available), and Claude Code stopped the second
judge queue to free memory; it held only the quantity arm, which will be judged once its screen lands.

**Quantity rows built; training started (22:55; job 783710, Hatem's account).** From the 14 batch reports (56
investigations on 28 new training companies), build_rows accepted **43** and refused 13 whose replay did not reach an
accepted finish (the teacher did not finish them; same rule as A's data). They give **1,046 rows** (sha256
6c611b23...), so the training set grows from A's 4,302 rows to 5,348 (sha256 92f5ca74...): +24% rows, and +27%
accepted investigations (158 to 201). Training at seed 7 with A's recipe (2 epochs, so about 24% more steps); then the
guards screen, judged against A seed 7.

**Second judge checked before test set 3 (00:55 Sunday; Hatem's plan).** One development packet (07ffe1f0..., from
the recovery round's seed-13 screen) judged by `claudecode` (claude-opus-5-5, Claude Code print mode, subscription
login, qualification `reports/judge/claudecode_score_qualification.json`): valid, 39 seconds. Scores run about a
point lower than codexsol170's on the same packet on framing and mechanism (mean of scored dimensions 1.43 against
2.00), consistent with the earlier finding that the judges agree on order but not on level, which is why test set 3
compares arms within each judge and then averages. At this speed with 4 workers, test set 3's roughly 250 packets take
about 40 minutes for this judge. The check judgment is kept apart (`judge_results/claudecode_check_22nov/`) and enters
no result.

**Hugging Face: a new organisation with credits, and Hatem's choices (04:05 Sunday).** Hatem was invited into
`twoeyedravens` (Two-eyed Ravens; 3 members; about $100 of credits, balance visible only on its billing page), distinct
from `two-eyed-ravens`, which holds the published Stage 1 model and dataset. His choices: (1) Stage 2's artifacts
(A's adapter, training rows, development reports, blind packets and judgments) go to `twoeyedravens` **public now**;
test set 3's data stays private until Monday's run, so the test cannot leak before it is run; files are scrubbed as
for the GitHub release (no personal data or paths, no notes about AI assistants' work). (2) Stage 1's model and
dataset are **copied** to `twoeyedravens` and also kept in `two-eyed-ravens`. (3) Credits: a demo Space running A on
an L4 that sleeps when idle, and a free CPU Space to browse every development run and judgment. Running part of test
set 3 on Hugging Face hardware is **not** done (Hatem: "skip the monday set up"): all three arms stay on the cluster's
identical server setup, as registered, so no hardware difference enters between arms. Blocked until Hatem's token
has write access to `twoeyedravens`.

**Quantity condition trained (04:10 Sunday; job 783710, Hatem's account).** A's rows plus the 1,046 quantity rows
(5,348 in all, sha256 92f5ca74...), A's corrections as extras, seed 7, A's recipe: 2,494 steps (A: 1,971), 5.3 hours;
held-out loss on the same 240 validation rows 0.575 at step 50 and 0.380 at the end (A: 0.565 to 0.387); adapter
sha256 320dba8af70d9a5c... The guards screen (job 784124) started at
04:15; judged against A seed 7, appendix only.

**Quantity condition judged (07:30 Sunday; job 784124; one seed, appendix only).** A's data plus 43 accepted
Command A+ investigations on 28 new training companies (+27% investigations, +24% rows), seed 7: 36 of 45 finished
(A: 39), 67 refused calls (146), median 33 turns (35); 23 packets for 45 runs. Quality **2.09 against A seed 7's 2.01:
+0.09 [−0.02, +0.19]**, higher at 5 of 6 companies (ACR −0.26); by dimension, revision +0.25, experiment design +0.24,
evidence judgement +0.22, assumptions +0.19, recommendation +0.12, problem framing −0.10, seeking challenge −0.13.
Against the prompted 8B +0.80 [+0.64, +0.94]. Reading: more data of the same kind gives a small, inconclusive gain at
one seed; the two recovery conditions also gained at seed 7 and did not replicate, so no claim is made beyond direction
and size. Merged files: `stage2ab_all`; `scripts/paper/check_numbers.py` still passes on them (no printed value moved).
Development is complete.

**Test set 3: configuration frozen, run started (Sunday 22 November, before any test set 3 run).** Hatem: run test set
3 today rather than Monday; nothing in the registered rules requires Monday (A was confirmed on 21 November at 08:55
against every registered condition, and every development result is in, so no other configuration can become
eligible). Preflight on code e3a19cc passed all 16 checks: test cases and dossier identical on both accounts to the
frozen local files (digest 068261a9), A's seed-7 adapter identical on both (490d47e3...), AgentTune and AuditKIT in
both environments, the Stage 1 system's files present. The full configuration is `docs/test3_config.json`, committed
here before the run. Arms, 48 cases x 2 attempts: A (Nour's account), the prompted 8B on the same scaffold and the
Stage 1 system (Hatem's account); one blind shuffled packet set; both judges; `scripts/test3/analyze.py` as registered.

**Test set 3, first attempt cancelled; rerun on a fresh deploy (13:50 Sunday).** The first attempt used code e3a19cc
(the development screens' copy), but the screen job's split option (`SPLIT`, commit 9d42bad, Monday preparation) came
after it: the A arm's runner was given test set 3's case names under the development split, found none and exited
having run no investigation; the prompted arm had not started; the Stage 1 arm (whose job already took the split) had
run 3 minutes. My error: the plan said to run on a fresh deploy, and I reused the old copy; the preflight did not check
the split. Both remaining jobs were cancelled and every file of the attempt set aside unread
(`runs/screen/test3_attempt1_cancelled/`, `runs/eval/test3_attempt1_cancelled/`, `experiments/test3/attempt1_cancelled/`);
none enters any result. A second bug surfaced too: the run script's wait loop lost its job list to ssh reading stdin,
so it moved on before the jobs ended; fixed with `ssh -n`. Fresh deploy 49fe311 to both accounts (agent, tools, guards
and runner unchanged since e3a19cc); the preflight, now also checking the split, passed all 18 checks;
`docs/test3_config.json` updated to 49fe311 and committed before the rerun. All three arms run again on this code.

**Hugging Face access and the Stage 1 copy (14:03 Sunday).** Hatem re-authorised the local Hugging Face login with
`twoeyedravens` ticked: role write, prepaid billing that can pay. Stage 1's model and dataset were copied as they are,
public, to `twoeyedravens/aemon` (10 files) and `datasets/twoeyedravens/aemon` (308 files); the originals in
`two-eyed-ravens` are unchanged. Test set 3's rerun is running: A's first investigations were written with no runner
error, so the split fix holds.

**Everything moved to `twoeyedravens` (Hatem: "deploy everything to the new org because i want to delete the old
one", 14:09 Sunday).** On Hugging Face: Stage 1's model and dataset copied (`twoeyedravens/aemon`), their cards'
links pointed at the new org; Stage 2's adapter A and every development run and judgment published
(`twoeyedravens/aemon-8b`, model and dataset; built by `scripts/release/build_release_stage2.py`, 0 identifiers left, no
test set 3 file, MANIFEST.json with sha256 of source and copy); a new collection holding both stages and the demo
Space; and the organisation page (`spaces/twoeyedravens/README`, source `deploy/hf_org/README.md`, now covering
Stage 2). Repository links (README, public README, cards, article text, Space README, paper) point to the new org;
this log keeps the old names as history. Not movable by API and left to Hatem: the posted article
(blog/HatemSaadallah/aemon) links to `two-eyed-ravens`, so its links break once the old org is deleted unless edited
by hand; deleting `two-eyed-ravens` also ends the redirects from the old names. The demo Space stays under Hatem's
account and is unaffected.

**Correction and a decision (14:12 Sunday).** Three of today's entry times were estimated rather than read (13:55,
14:25, 14:45); each is now its commit time (13:50, 14:03, 14:09). Hatem: keep `two-eyed-ravens` for now, for its
redirects; it is not deleted, and its repos stay as they are alongside the copies in `twoeyedravens`.

**Stage 2 paper published to the public repository (14:55 Sunday; Hatem: "Public repo, paper only, now").** Commit
fbbecfc on github.com/Two-Eyed-Ravens/aemon (main) adds `docs/stage2/PAPER_STAGE2.pdf` with its LaTeX source and
figures, everything up to now, with test set 3 marked pending; no other file changed. Scanned before the push: no
cluster identifiers or home paths, no notes about AI assistants' work (the judges keep their names). Committed as
Hatem with his noreply address, no co-author line. The paper is replaced there once test set 3 is analysed; the full
public snapshot follows after that, as planned.

**Test set 3: runs complete, judging in parallel (17:31 Sunday).** All three arms ran on code 49fe311 with AuditKIT:
finished investigations (mechanical, before any judgment) A 81 of 96, the prompted 8B on the same scaffold 2 of 96,
the Stage 1 system 82 of 96. One blind shuffled packet set: 223 packets from 288 runs. Codex (codexsol170) started
from the run script; at Hatem's request the Claude Code judge (claudecode) runs at the same time on the same packets
into the same output folder, instead of after it, which changes nothing in what either judge sees. Then
`scripts/test3/analyze.py` as registered.

**Test set 3: the two invalid Claude Code judgments are re-judged (Hatem, 17:42 Sunday; a deviation from the
registered rule, recorded before any test set 3 score was computed or seen).** The registered reading leaves runs a
judge cannot score validly out and does not re-judge them. Two claudecode answers (packets efcb15d59439b873 and
e0303ce718579ca9) failed the instrument's check with "dimension set differs": the answer's set of rubric dimensions did
not match the rubric's nine, a formatting failure, not a verdict. Hatem asked to repeat them. They are re-judged once,
through the instrument's resume path after the claudecode campaign ends (the failed results kept in
`judge_results/test3/claudecode_invalid_first/`); if a second attempt also fails, that packet is left out as
registered. Reported in the paper as a deviation. No result of test set 3 had been computed when this was decided.

**TEST SET 3 RESULT (18:05 Sunday; read exactly as registered, `scripts/test3/analyze.py`; `experiments/test3/report.json`).**
Twelve companies never used before, 48 cases, 2 attempts, 96 runs per arm, both judges (codexsol170 and claudecode),
all 288 runs scored by both (the three claudecode answers that failed the instrument's format check were re-judged
once at Hatem's request, all valid; recorded above as a deviation). Mean of judges per arm: **A 1.71, Stage 1 system
1.58, prompted 8B on the same scaffold 1.01**; finished runs A 81, Stage 1 system 82, prompted 8B 2 (of 96).

| Comparison (paired by case and attempt) | Mean of judges | Company t-interval (12) | Codex | Claude Code | Companies above 0 |
|---|---|---|---|---|---|
| **A minus prompted 8B** (primary) | **+0.70** | **[+0.61, +0.79]** | +0.79 [+0.66, +0.93] | +0.61 [+0.52, +0.70] | 12 of 12 |
| A minus Stage 1 system | +0.12 | [+0.05, +0.20] | +0.19 [+0.04, +0.34] | +0.06 [+0.01, +0.11] | 10 of 12 |

Company bootstrap: [+0.62, +0.78] and [+0.06, +0.19]; case bootstrap [+0.65, +0.76] and [+0.08, +0.17]. Secondary,
shared stages only: +0.55 [+0.44, +0.66] and +0.13 [+0.04, +0.22]. The judges agree in sign on both comparisons;
Spearman 0.78 between their run scores, mean absolute difference 0.45. Reading under the registered rule (interval over
companies): fine-tuning Aya Expanse 8B on the teacher's trajectories improves judged investigation quality over the
same model prompted with an identical scaffold on companies never seen in development or training, by about +0.7 on
the 0 to 3 rubric (development: +0.72 to +0.88), and the 8B system is above Stage 1's Tiny Aya system by a small,
interval-clear margin. Run once; not re-run. Files: `experiments/test3/` (reports of the three arms, the blind packets,
the key, both judges' predictions, the analysis).

**Test set 3: Claude Haiku 5.5 as a fourth arm (Hatem, 22 November ~19:00; registered before the run; a comparison
added after the three-arm result, reported as such and leaving that result unchanged).** Asked by an outside review:
the open question is how the fine-tuned 8B compares with a closed model on these cases. Rule:
- Haiku 5.5 through the same environment and tools, settings as Stage 1's registered Haiku baseline (13 November:
  `--backend claude --claude-model claude-haiku-5-5 --prompt staged`, default effort), on the same 48 test set 3
  cases x 2 attempts (`--split heldout3`), agent and environment code unchanged since 49fe311; cost capped at $5.
- Packets rebuilt from all four arms' reports; judgments of packets already judged are reused by packet id, and only
  Haiku's new packets are judged, blind, by both judges (codexsol170 and claudecode). An answer that fails the
  instrument's format check is re-judged once, as for the three arms.
- Reading: `scripts/test3/analyze.py` unchanged, comparisons Haiku minus A (primary of this addition) and Haiku minus
  the Stage 1 system; mean of judges, company t-interval over 12 companies. Whatever it shows goes into the paper
  and README, with cost per investigation.

**Correction to the 17:42 re-judging entry (recorded 22 November, 18:55).** That entry named two invalid claudecode
packets (efcb15d59439b873, e0303ce718579ca9). A third (9f6d06d3a5bcc397) failed the same format check later in the same
campaign, before any test set 3 score was computed, and was re-judged once under the same rule; the result entry lists
all three. The paper says so.

**Test set 3, Haiku arm: 22 of 96 episodes lost to Anthropic API errors (19:00 Sunday, before any Haiku packet was
built or judged).** Every one ended in `anthropic.InternalServerError: 500` after the SDK's retries, as in Stage 1's
Haiku run (13 November), so they are rerun once each by the same rule (`experiments/test3/haiku/rerun.sh`, a copy of
`experiments/haiku/rerun.sh`) and merged; any still lost are reported as lost. The 74 runs that ended normally (60
finished) are kept as they are. AuditKIT was skipped at run time (the laptop environment lacks AgentTune, which its
replay imports); it is run on the saved trajectories in the cluster's training environment, as for the eleven
development reports. API cost of the first pass: $0.62.

**Test set 3 Haiku arm: invalid judgments re-judged once (22:40 Sunday, before any Haiku score was computed).** Of the
91 new packets, claudecode returned 33 invalid answers: 31 "Claude Code invocation failed" (the CLI exited non-zero
after its answer, during an account usage limit; not judgments) and 2 "dimension set differs"; codexsol170 returned 1
(an accepted trajectory with a critical red flag, which the instrument rejects). As registered for this arm, each is
re-judged once; the first attempts are kept in `judge_results/test3_haiku/invalid_first/`. AuditKIT on the merged
Haiku report (cluster job 786076, training environment): 0 replay mismatches.

**TEST SET 3, HAIKU ARM RESULT (23:00 Sunday; read as registered, `experiments/test3/haiku/analyze.sh` ->
`scripts/test3/analyze.py`; `experiments/test3/haiku/report.json`).** Claude Haiku 5.5 through the same environment,
Stage 1's settings: 91 of 96 runs (5 lost twice to API errors), 70 finished; AuditKIT 0 replay mismatches; $0.74 in
all, $0.008 per investigation. After one re-judge of failed answers, 3 Haiku packets lacked a valid judgment from one
judge and are left out (88 paired runs). Mean of judges: Haiku 1.92, A 1.71, Stage 1 system 1.58, prompted 8B 1.01.

| Comparison | Mean of judges | Company t-interval (12) | Codex | Claude Code | Companies above 0 |
|---|---|---|---|---|---|
| Haiku minus A | +0.20 | [+0.05, +0.35] | +0.12 [−0.08, +0.31] | +0.30 [+0.20, +0.41] | 9 of 12 |
| Haiku minus Stage 1 system | +0.33 | [+0.17, +0.48] | +0.32 [+0.12, +0.52] | +0.36 [+0.27, +0.46] | 10 of 12 |

Shared stages: +0.44 and +0.56. Reading: the closed model is still ahead of the fine-tuned 8B on judged quality, by a
small margin whose interval is clear of zero under the mean of judges but not under Codex alone; the gap is about a
third of Stage 1's (final system minus Haiku −0.67 and −0.63). The fine-tuned 8B finishes more runs (81 of 96 against
70 of 91). Added after the three-arm result, as registered.

**Haiku arm: 11 runs ended on API refusals; a second reading, post hoc (23 November, after an outside review).** In
11 of Haiku's 91 test set 3 runs the API returned `stop_reason: "refusal"` with no output on the last three or four
turns; the harness logged each as invalid JSON and stopped the run as "repeated errors" (Stage 1's 120 Haiku runs had
none; for 9 of the 11 the other attempt at the same case finished). The registered result stands: Haiku minus A
+0.20 [+0.05, +0.35]. They are not rerun: the HTTP 500 rule covers server errors, which are not the model's behaviour,
and a refusal is the model's own response, so rerunning until it answers would bias the comparison toward Haiku. Read
post hoc, with those 11 runs left out (77 pairs): Haiku minus A +0.42 [+0.32, +0.52] (Codex +0.35 [+0.21, +0.50],
Claude Code +0.49), higher at all twelve companies; Haiku minus the Stage 1 system +0.55 [+0.46, +0.63]; Haiku then
finishes 70 of 80. Both readings are reported. Haiku ran with Stage 1's registered settings: the staged prompt, effort
medium, none of the six decoding guards. `experiments/test3/haiku/report_without_refusals.json`.

**Test set 3: the fine-tuned 8B without guards as a fifth arm (Hatem, 23 November; registered before the run; added
after the main result, reported as such and leaving it unchanged).** An outside review noted that the paper's title
claim, that the fine-tuned weights and the guards are complements, rests on development data (one seed, one judge).
Rule:
- A (adapter seed 7) with no decoding guards (`ARMS=none`), otherwise exactly as test set 3's A arm: code 49fe311,
  `jobs/screen_bases.sbatch`, the same bf16 base and adapter, compact prompt, context 8192, `SPLIT=heldout3`, the same
  48 cases x 2 attempts, the same account and environment.
- Packets rebuilt from all arms' reports; judgments of packets already judged are reused by packet id; only the new
  packets are judged, blind, by both judges (codexsol170 and claudecode); an answer that fails the instrument's check
  is re-judged once.
- Reading: `scripts/test3/analyze.py` unchanged, comparisons A minus A-without-guards (primary of this addition) and
  A-without-guards minus the prompted 8B; mean of judges, company t-interval over 12 companies; finished runs
  reported. The complements claim holds on held-out data if A minus A-without-guards has its interval above zero;
  whatever it shows goes into the paper, README and slides.

**TEST SET 3, GUARDS-OFF ARM RESULT (23 November 03:23; read as registered, `experiments/test3/noguards/run_after.sh`
-> `scripts/test3/analyze.py`; `experiments/test3/noguards/report.json`).** A without guards, 96 runs (job 786573, code
49fe311): 34 finished (57 stopped on repeated errors, 5 at the turn limit), 77.1% of calls accepted. 86 new packets,
all judged validly by both judges at the first attempt; all 384 runs scored by both. Mean of judges: A 1.71, A without
guards 1.23, prompted 8B 1.01, Stage 1 system 1.58.

| Comparison | Mean of judges | Company t-interval (12) | Codex | Claude Code | Companies above 0 |
|---|---|---|---|---|---|
| A minus A without guards (primary of this addition) | +0.48 | [+0.31, +0.65] | +0.50 | +0.46 | 12 of 12 |
| A without guards minus prompted 8B (with guards) | +0.22 | [+0.01, +0.43] | +0.29 | +0.15 | 10 of 12 |

Shared stages: +0.11 [+0.02, +0.20] and +0.56. Reading under the registered rule: the interval of A minus A without
guards is above zero, so the complements claim holds on held-out data: the guards add +0.48 to the fine-tuned model
(finished 81 against 34), and the fine-tuned weights without guards are still above the prompted model with guards.

**Test set 3: two more prompted-8B arms (Hatem, 23 November ~11:50; registered before their runs; added after the
main result, reported as such and leaving it unchanged).** An outside review asked for the complete weights-and-guards
grid on one scaffold, held out, and for the best-prompt baseline on test set 3. Both run exactly as the prompted arm
(code 49fe311, `jobs/screen_bases.sbatch`, the same bf16 base, no adapter, context 8192, `SPLIT=heldout3`, 48 cases x 2
attempts):
- **prompted 8B, compact prompt, no guards** (`PROMPT=compact ARMS=none`): with A, A without guards and the prompted 8B
  with guards it completes the 2x2 on the compact scaffold.
- **prompted 8B, staged prompt with guards** (`PROMPT=staged ARMS=guards`): its best development configuration (27 of 45
  finished; the +0.60 baseline).
Judged blind by both judges as for the earlier added arms (existing judgments reused by packet id; a failed answer
re-judged once); `scripts/test3/analyze.py` unchanged with A minus each new arm, and A-without-guards minus
prompted-compact-without-guards (does the fine-tuned model need fewer guards than the base?). Jobs are submitted with
5-hour limits because the queue estimates a start after the deadline; if they have not finished in time for the
submission they are reported later, not partially.

**TEST SET 3: PROMPTED 8B, COMPACT PROMPT, NO GUARDS (23 November 14:16; read as registered,
`experiments/test3/prompted_more/run_after.sh` -> `scripts/test3/analyze.py`; `.../P_compact_none/report.json`).** Job
787455: 1 of 96 finished (95 stopped on repeated errors), 72.7% of calls accepted. 47 new packets, all judged validly
by both judges at the first attempt; every run scored by both. Mean of judges 0.87. The 2x2 on the compact scaffold,
held out (mean of judges; finished of 96):

| | No guards | Six guards | Guards add (company t-interval) |
|---|---|---|---|
| Prompted 8B | 0.87 (1) | 1.01 (2) | +0.14 [+0.02, +0.25], 8 of 12 companies |
| Fine-tuned 8B (A) | 1.23 (34) | 1.71 (81) | +0.48 [+0.31, +0.65], 12 of 12 |
| Fine-tuning adds | +0.36 [+0.16, +0.55], 11 of 12 | +0.70 [+0.61, +0.79], 12 of 12 | |

A minus the prompted 8B without guards: +0.84 [+0.70, +0.98], 12 of 12. Reading: on held-out companies each part makes
the other worth more: the guards add more to the fine-tuned model than to the prompted one, and fine-tuning adds more
with the guards than without. The complements claim now rests on all four cells of one scaffold, held out.

**Test set 3, staged-prompt arm: Claude Code judging repeated after a billing block (23 November ~18:10).** Every
claudecode call on the arm's 62 new packets, first attempt and the registered re-judge, returned HTTP 403 ("can't use
your Claude subscription, usually because a payment is past due") before any answer: no judgment was produced, so
neither attempt counts. After Hatem paid, the 62 packets are judged again; the failed attempts are kept in
`judge_results/test3_P_staged_guards/`. A preliminary Codex-only reading (A minus this arm +0.64 [+0.51, +0.77]) was
computed while waiting and is not the registered result.

**TEST SET 3: PROMPTED 8B, STAGED PROMPT WITH GUARDS, ITS BEST CONFIGURATION (23 November ~18:45; read as registered;
`experiments/test3/prompted_more/P_staged_guards/report.json`).** Job 787456: 48 of 96 finished (39 at the context
limit, 9 on repeated errors), 95.7% of calls accepted. 62 new packets: codexsol170 all valid; claudecode, after the
billing block above, 61 valid and 1 re-judged once (valid). Every run scored by both judges. Mean of judges 1.17.
A minus this arm: **+0.54 [+0.46, +0.62]**, 12 of 12 companies (Codex +0.64, Claude Code +0.44); on shared stages +0.51
[+0.43, +0.60]. A without guards minus this arm: +0.06 [−0.12, +0.24], inconclusive. Reading: against the prompted
8B's best prompt the fine-tuned agent still leads by about half a point at every held-out company.

**Quality at 4 bits: the bench's promised judging (27 November; registered before any packet is built).** The 19
November bench rule said the fastest qualifying setting "then gets the blind judge"; it never did, and an outside
review noted that the paper's cost ($0.019 per investigation) is at 4 bits while every quality number is at bf16.
Checked first: the bench (job 776913, code 1a8e7ab) merged `runs/base_aya-expanse-8b/adapter`, whose weights
(adapter_model.safetensors 8c444fb0...) and served GGUF (490d47e3...) are identical on both accounts to test set 3's A.
Rule:
- Primary: Q4_K_M minus bf16, both merged and both served 8 at once (`experiments/bench/q4_k_m_s8.json`,
  `bf16_s8.json`; the same 15 development cases x 3 attempts, guards, compact prompt). Only quantization differs.
- Secondary: merged bf16 at 8 at once minus the LoRA arm A seed 7 (`experiments/screen/aya-expanse-8b-s7_guards.json`),
  i.e. merging plus batching.
- Blind packets from the three reports (`aemon.evaluation.judging.packets --split development`), judged by both judges
  (codexsol170, claudecode; a failed answer re-judged once); `scripts/test3/analyze.py` unchanged (mean of judges,
  company t-interval, here over 6 companies); finished runs and refused calls reported beside. "No loss" means the
  lower bound of Q4_K_M minus bf16 is above −0.15. Outputs in `experiments/bench/judging/`; frozen files untouched.

**Test set 3: A in its cost configuration as one more arm (27 November; registered before the run).** The
configuration behind the paper's $0.019 per investigation, A merged and quantized to Q4_K_M and served 8 at once, run on
test set 3 (`jobs/inference_bench.sbatch` at 0aea312 with `PRECISIONS=q4_k_m SLOTS=8 SPLIT=heldout3 ATTEMPTS=2` and the
48 cases; the same adapter, 8c444fb0... / 490d47e3..., merged; agent and environment code unchanged since 49fe311).
Packets with A and the prompted 8B, existing judgments reused by packet id, the new packets judged blind by both judges
(a failed answer re-judged once); `scripts/test3/analyze.py` unchanged: this arm minus A (primary; serving at 4 bits,
merged, 8 at once, against the evaluated bf16 LoRA at one at a time) and this arm minus the prompted 8B. "No loss":
lower bound of this arm minus A above −0.15. Finished runs and refused calls reported beside. Outputs in
`experiments/test3/q4/`.

**QUALITY AT 4 BITS, DEVELOPMENT (27 November 18:40; read as registered; `experiments/bench/judging/report.json`).**
134 packets from the three reports, all judged validly by both judges at the first attempt. Mean of judges: Q4_K_M
merged at 8 at once 1.73 (39 of 45 finished, 98 refused calls, 92.8% accepted), bf16 merged at 8 at once 1.71 (37, 132,
91.9%), the LoRA arm A 1.72 (39, 146, 91.2%). Primary, Q4_K_M minus bf16: +0.01 [−0.17, +0.20] over 6 companies
(Codex −0.02, Claude Code +0.05): no detectable difference, but the lower bound is below −0.15, so "no loss" is not
established by this reading; the interval is wide with six companies. Secondary, merged bf16 minus LoRA: −0.00
[−0.09, +0.09]: merging and batching change nothing measurable. Also computed, not registered: Q4_K_M minus LoRA
+0.01 [−0.12, +0.14]. The held-out arm (job 796248) is the reading that can settle it.

**Codex judge account change (27 November ~19:40).** Hatem logged the Codex CLI out of Nour's ChatGPT account and into
his own (Edu plan) before the 4-bit arm's judging. The judge itself is unchanged: the pinned codex-cli 0.170.0 binary
(sha256 880819aa...), the model gpt-6-sol and the settings in `backends_v1.json`. Every earlier Codex judgment used
Nour's account. The local watcher was paused while logged out and restarted after; the cluster job was unaffected.

**Offline harness optimization foundation (27 November 21:19 UTC).** Start with declarative recovery candidates
and paired development evaluation. A candidate selects existing reviewed features through a frozen, validated JSON
model in `src/aemon/evaluation/harness/candidate.py`. Unknown fields and unsupported features are rejected;
`evidence_first` requires `quote_menu`. Candidate identity includes its canonical feature selection and name.

The new package entry point, `python -m aemon.evaluation.harness`, validates candidates or runs them against a fixed
baseline through the existing guarded investigation loop. Each arm starts fresh, using the compact prompt, 45 turns,
four consecutive errors, 520 output tokens, quote normalization enabled, and attempt 0. This first runner explicitly
disables adapters for both arms. Cases must belong to the requested training or validation company partition within
development. The runner records source, test and dossier digests, revision, candidate identity, operator-supplied
runtime description, full episode records, recomputed mechanical checks, and token totals. Exclusive output creation
protects prior results; a completion row distinguishes a finished campaign from a partial file.

This establishes the input contract and evaluation entry point for future bounded search. A promotion rule still
requires independent blind quality review in addition to mechanical validity. Runtime descriptions require operator
verification. Before executable candidate patches are accepted, introduce separate restricted optimizer, execution,
and evaluator processes, protect evaluator inputs, and pin an independent progress definition. Model-backed paired
measurements and automated search remain future work.

Validation at this step used the harness tests plus recovery, grounding, verification, experiment-design and test-set
freeze suites: **31 passed in 3.12 seconds**. Ruff check and format verification passed on the added Python files;
Pyright reported **0 errors, 0 warnings** for the added package and tests. Pytest was installed into the local project
environment through uv. Package usage is documented in `src/aemon/evaluation/harness/README.md`.

Both existing HPC accounts were inspected after VPN connectivity was restored. Both can access the `stud` partition,
which advertises 40 GB and 80 GB GPU resources, with a maximum job time of 1 day and 10 minutes. Neither account had
queued or running jobs in the inspected output. The primary experiment workspace has Tiny Aya bf16 weights, prior
evaluation adapters, a llama.cpp server binary, and a main environment containing pytest, Torch and AgentTune. The
secondary workspace has a llama.cpp server binary, Qwen experiment artifacts and a smoke adapter; its main environment
contains Pydantic but lacks pytest, Torch and AgentTune. Its separate training environment contains all four
packages. These observations support using the primary workspace for an initial reproducible campaign. Shared filesystem free space does not establish either account's quota. This step
performed remote inspection only.

**Bounded recovery-policy experiment registered (27 November, before new inference).** Compare the strongest
fine-tuned 8B's six recovery features with three additions, individually preregistered in
`experiments/harness/recovery_v1/`: reread masking, structured progress feedback, and both. Selection cases are six
training companies chosen by a deterministic hash of company names, with the case within each company selected by a
hash of its ID, independently of model outcomes. Exact cases and attempts are in `protocol.json`. Each candidate is
paired with the full baseline on the six cases at attempt 7. Eligibility requires no decrease in completion or
mechanical guard clearance, no increase in simulated-citation refusals, and an efficiency improvement. Rank eligible
candidates by total prompt plus completion tokens, then calls, then name. If none qualifies, record the rejection.

Compare the selected candidate with the baseline on the established 15 validation cases at attempts 7, 8 and 9.
These companies have already supported development choices, so this is a development experiment. Independent blind
quality review is required before promotion. Inference uses the same merged Aya Expanse 8B Q4_K_M weights as the cost
configuration, with a full weights hash check, context 8,192, one server slot, the compact prompt, 45 turns, four
consecutive errors, and 520 output tokens. Both arms share all decoding settings. Count repeat-redraw inference in
token totals. Single-slot latency supports within-experiment comparisons. The six-hour Slurm job bound covers model
preparation and at most 126 investigations. The original evaluated configuration remains the baseline for this work.

The accompanying interface will show recorded policy differences, paired metrics and traces, with provisional
selection distinguished from independently reviewed quality. Claude judging is pending its subscription limit reset,
as requested. Existing Q4 quality coverage is incomplete and cannot yet support the registered two-judge claim.

**Q4 held-out judging coverage checked (27 November).** The completed inference run finished 79 of 96 investigations,
with 293 refused calls, against A's 81 and 274. The first judge scored all 96 new packets; the second scored 18.
All remaining 78 packets have two preserved HTTP 429 usage-limit failures with zero tokens and no answer. Their
recovery remains pending user confirmation of availability, following the existing zero-output transport precedent.
The current mean-of-judges Q4-minus-A comparison uses only 18 pairs from nine companies, -0.145 [-0.290, +0.000].
It cannot establish the registered lower-bound-above--0.15 criterion. The unchanged analyzer reproduces the report
exactly. Evidence is in `experiments/test3/q4/consolidation_evidence.json`. The development cost estimate and the
held-out incomplete quality result retain their distinct populations and serving conditions.

**Work stopped at user request (27 November 21:27 UTC).** Implementation is paused with an uncommitted checkpoint.
The original foundation's 31 passing tests and targeted clean lint/type checks predate the new runner and interface
drafts. The existing app API/auth/company suites also passed 32 tests during this session. Those results do not
validate the unfinished integration described below.

Changes since the foundation include draft runtime identity checks in `evaluation/harness/runtime.py`, runner/CLI
extensions, and redraw usage aggregation in `agent/loop.py`. A draft `evaluation/harness/campaign.py` adds bounded
selection orchestration. The preregistered candidate files and protocol are in `experiments/harness/recovery_v1/`,
and `jobs/harness_recovery.sbatch` contains the proposed six-hour model-preparation and evaluation job.

The new interface draft consists of `app/harness_experiments.py`,
`app/web/src/pages/HarnessPage.tsx`, and navigation/routing changes in `app/web/src/App.tsx`. The backend router has
not been registered in `app/server.py`. The interface, API data layout and campaign output still need integration
and validation. A full frontend build and nested-display visual check remain pending.

Known blocking mismatch at this checkpoint: the draft campaign's BASE_FEATURES uses `citations`, while the registered
baseline correctly uses `resample_repeats`. Reconcile the implementation with the registered six features before
running inference. The Slurm draft also lacks the new campaign CLI's required runtime-expectation and model-receipt
arguments. Its expected-runtime JSON and externally checked model-hash receipt must be generated and supplied.
Candidate schema support, CLI signatures, redraw accounting, campaign selection and partial-output handling all need
review and tests together. Campaign tests have not yet been written. Runtime metadata is reported evidence with an
operator receipt, not independent remote attestation.

No new HPC job, model evaluation, optimizer search, quality-judging retry, deployment, or publication was started in
this work. Both HPC accounts were inspected only. The pending Q4 analysis is documented in
`experiments/test3/q4/README.md`, `consolidation_evidence.json`, and `validation_report.json`; its original report
was reproduced exactly and remains incomplete. Claude judging stays pending the user's availability signal.
Local environment additions through uv include pytest, httpx2 and a requested Playwright installation; final
Playwright installation status was not rechecked at stop. A new root `uv.lock` appeared during tool invocations and
is outside the intended deliverables; review its provenance before retaining it. Finish targeted formatting, lint,
type checks, regression tests, frontend build and API integration before treating these drafts as usable.

Worker stop receipts confirmed the runner now permits `resample_repeats` and its five touched Python files passed
Ruff formatting and lint. Updated runner tests have not run, and its targeted type check did not execute. The app's
pre-change TypeScript check passed; post-change frontend checks have not run. The draft backend reader is known to
be incompatible with the campaign format and must be adapted before router registration. All delegated workers
reported stopped, with no background compute or evaluation processes launched.

**TEST SET 3, A IN ITS COST CONFIGURATION (27 November 23:20; read as registered; `experiments/test3/q4/report.json`).**
Job 796248 (code 0aea312; Q4_K_M weights sha256 5ad8d535..., the same file as the development bench's). 96 runs: 79
finished (A 81), 293 refused calls (A 274), 90.7% of calls accepted (A 92.4%). Judging: Codex scored all 96 new
packets (now on Hatem's account, same pinned judge); Claude Code scored 18, and 78 returned HTTP 429 usage-limit
responses with zero output twice. After the limit reset (23:00) those 78 were judged once more, all valid; the 429
attempts are kept under `judge_results/test3_A_q4/transport_429/` (the transport precedent: no answer was produced, so
nothing was discarded). Mean of judges: Q4 arm 1.59, A 1.71, prompted 1.01. Primary, Q4 arm minus A: **−0.12 [−0.19,
−0.06]** over 12 companies (Codex −0.09, Claude Code −0.16), lower at 11 of 12: "no loss" is not met, and the loss is
detectable. Q4 arm minus prompted: +0.58 [0.51, 0.64], higher at 12 of 12. The arm changes three things at once (4 bits,
merged, 8 at once); on development, merging and batching changed nothing measurable (−0.00 [−0.09, +0.09]), so the
loss is most likely the 4-bit quantization, but this reading alone does not separate them. Reading for the paper: the
$0.019 per investigation configuration scores 0.12 below the evaluated model and still 0.58 above the prompted 8B.

**Harness work finished from Codex's checkpoint (27 November 23:30; before any inference).** Codex stopped at Hatem's
request with four items open. Fixed: the campaign's fixed baseline listed `citations` where the evaluated six guards
(and `baseline.json`) have `resample_repeats`, so the campaign would have refused its own baseline; a test now loads
the registered protocol as the campaign does. Two stale tests updated (`resample_repeats` is an allowed feature; the run
command now requires `--expect-runtime`). The cluster job did not pass the runtime expectation the campaign requires:
it now records the server's identity once at start (model path and id, build, context, chat template hash, quantization,
slots) with a receipt for the weights hash it checks itself, and every paired run refuses a server that differs. The
protocol, candidates, cases, attempts and selection rule are unchanged. Harness tests 13 passed; ruff and pyright clean.

**HARNESS RECOVERY SELECTION, READ AS REGISTERED (28 November; job 796519, code d6d2928, 44 minutes).** Weights checked
against the evaluated Q4_K_M hash; server identity recorded at start and checked on every paired run. On the 6 training
cases at attempt 7, the six-guard baseline finished 5 of 6 with 456,755 tokens and 159 calls (identical in all three
pairs: the runs are deterministic). Each candidate finished all 6 but spent more: reread masking 494,437 tokens (+8%),
progress feedback 606,690 (+33%), both 550,653 (+21%). No simulated-citation refusals anywhere; no finished run cleared
every mechanical gate in any arm (each fails one or two strict gates, such as `evidence_kinds`). The registered rule
needs an efficiency gain, so no candidate is eligible: the baseline stays, and the validation stage was skipped as the
protocol says. Reading: the loop ran end to end and refused changes that did not pay for themselves; the one signal
worth a follow-up is that every candidate finished the run the baseline did not, at a token cost. Results in
`experiments/harness/recovery_v1/results/`, shown on the app's harness page.

**Stage 2 submission prepared (28 November; organisers' reminder: deadline Sunday 29 November 11:59 UTC).** Hatem lost
write access to `twoeyedravens` and asked for everything in `two-eyed-ravens`. Copied there: model and dataset
`aemon-8b` (cards' links rewritten, data untouched), the 4-bit `aemon-8b-GGUF` (transferred by Hatem; sha256 5ad8d535...
checked), the Stage 1 cards. The live demo stays at `spaces/twoeyedravens/aemon-8b`: a Docker Space in
`two-eyed-ravens` needs a paid Team plan (HTTP 402), and the existing Space still runs. New public collections:
`two-eyed-ravens/aemon-models-6b0ad51a03322d756e80547e` and `two-eyed-ravens/aemon-datasets-6b0ad51c08e24bb8c2b8ee1b`.
Paper checked against the email: main body 6 pages; Limitations and Ethics sections added after the conclusion;
Aya Expanse and Tiny Aya now cited beside AgentTune and AuditKIT. Public GitHub snapshot 05c7636 (no personal data,
tokens or cluster identifiers found by scan); every README link returns 200.
