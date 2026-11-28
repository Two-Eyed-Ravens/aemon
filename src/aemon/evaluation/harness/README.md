# Offline recovery candidates

Candidates select reviewed recovery features through JSON. The evaluator fixes the
compact prompt, 45-turn budget, four-error limit, 520-token output limit, and seed
attempt 0. Both arms use the same llama.cpp server with adapters disabled.

Create a candidate file containing the following JSON.

```json
{"version": 1, "name": "budget-rereads", "features": ["budget", "mask_rereads"]}
```

Validate it through the package entry point.

```bash
uv run python -m aemon.evaluation.harness validate candidate.json
```

Run a paired evaluation against a separately provisioned llama.cpp server.

```bash
uv run python -m aemon.evaluation.harness run candidate.json \
  --partition validation --cases hellberg-new-evidence-looks \
  --url http://127.0.0.1:8091 \
  --runtime 'WEIGHTS_SHA256 QUANTIZATION CONTEXT SERVER_BUILD' \
  --out paired.jsonl
```

The baseline is `--baseline FILE`, or no recovery features without it. Each arm gets a fresh investigation. Only
development cases in the selected company partition are accepted. Candidate names
and features are validated, canonicalized, and hashed. Unknown fields, duplicate
features, and unsupported features fail validation.

The output starts with a manifest containing source, test, and dossier digests,
revision, candidate identity, and fixed settings. Episode rows contain tool logs,
checks recomputed by the evaluator, termination, and token usage. A final complete
row marks successful completion of the requested pairs. An interrupted file is
partial evidence. Output creation is exclusive, so a retry needs a new filename.

The runtime description is supplied by the operator. The runner does not attest
server weights or enforce a server context allocation. Keep the server and source
snapshot fixed throughout a campaign. Model inference requires allocated compute.

Mechanical guard clearance cannot establish strategic quality. Review full traces
and use independent blind quality evaluation before promotion. This foundation
supports declarative experiments. Code-patch search requires separate optimizer,
execution, and evaluator processes with restricted filesystem and network access.
