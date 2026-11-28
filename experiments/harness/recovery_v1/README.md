# Recovery policy selection

Registered before new inference. The experiment tests three additions to the
fine-tuned Aya Expanse 8B's existing six-feature recovery configuration. Each
candidate adds reread masking, structured progress feedback, or both.

All arms use the same merged Q4_K_M weights, server build, compact prompt,
8,192-token context, one server slot, temperature 0, 45 turns, four consecutive
errors, and 520 output tokens. Retry decoding follows the existing loop. Latency
comparisons apply within this experiment's single-slot runtime.

Training companies are chosen by sorting development training companies by
SHA256 of `harness-recovery-v1:` followed by their company name, then taking the
first six. Within each company, the case with the lowest SHA256 of its case ID is
selected. Case selection used identifiers without consulting model outcomes.
The exact case IDs and attempts are fixed in `protocol.json`.

Each candidate is paired with the baseline on those six cases at attempt 7.
Selection requires no decrease in completions or mechanical guard clearance,
no increase in simulated-citation refusals, and an efficiency improvement.
Eligible candidates are ranked by total prompt plus completion tokens, then
calls, then name. The complete selection rule is implemented in the trusted
campaign runner. If all candidates fail, the campaign records that outcome.

The selected candidate is compared with the baseline on the established 15
validation cases at attempts 7, 8 and 9. These validation companies have supported
prior development decisions, so the result measures development performance.
Independent blind quality review is required before any promotion. No selected
policy is automatically activated, and the frozen final-test suites are excluded.

Run artifacts include partial and completion receipts. A missing completion
receipt means the campaign is incomplete. The interface displays recorded
mechanical evidence and pending quality review separately.
