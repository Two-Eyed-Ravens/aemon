#!/bin/bash
# Preflight for the single test set 3 run (DECISIONS, 20 November). Read-only: checks files and hashes, never computes
# on the login node and never submits. Usage: scripts/test3/preflight.sh REVISION   (the code copy Monday's jobs use)
# Prints one line per check, PASS or FAIL, and exits non-zero if any check fails.
set -u
REV=${1:?code revision}
cd "$(dirname "$0")/../.." || exit 1
H() { ssh -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi" CLUSTER_ACCOUNT@CLUSTER_HOST "$1"; }
N() { ssh -o ControlMaster=no -o ControlPath="$HOME/.ssh/cm-lexsi2" CLUSTER_ACCOUNT_2@CLUSTER_HOST "$1"; }
FAILED=0
check() {  # name, command producing "ok" on success
  local out
  out=$(eval "$2" 2>&1 | tail -1)
  if [ "$out" = ok ]; then echo "PASS  $1"; else echo "FAIL  $1: $out"; FAILED=1; fi
}
FREEZE=$(python3 -c "import json; print(json.load(open('docs/test3_freeze.json'))['digest'])")
LOCAL_CASES=$(sha256sum data/dossier/cases_heldout3.json | cut -c1-64)
LOCAL_EVIDENCE=$(sha256sum data/dossier/evidence.json | cut -c1-64)
check "local freeze test (12 companies, 48 cases, digest ${FREEZE:0:8})" ".venv/bin/python -m pytest -q tests/test_test3_freeze.py >/dev/null && echo ok"
check "local code is committed and pushed" "[ -z \"\$(git status --porcelain src jobs scripts data)\" ] && [ \"\$(git rev-parse HEAD)\" = \"\$(git rev-parse origin/main)\" ] && echo ok"
for acct in H N; do
  check "$acct: screen job takes the test split (SPLIT)" "$acct 'grep -q SPLIT ~/lexsi/code_$REV/jobs/screen_bases.sbatch && echo ok'"
  check "$acct: code copy $REV present" "$acct 'test -f ~/lexsi/code_$REV/jobs/screen_bases.sbatch && echo ok'"
  check "$acct: test set 3 cases identical to local" "[ \"\$($acct 'sha256sum ~/lexsi/code_$REV/data/dossier/cases_heldout3.json | cut -c1-64')\" = $LOCAL_CASES ] && echo ok"
  check "$acct: dossier identical to local" "[ \"\$($acct 'sha256sum ~/lexsi/code_$REV/data/dossier/evidence.json | cut -c1-64')\" = $LOCAL_EVIDENCE ] && echo ok"
  check "$acct: llama-server built" "$acct 'test -x ~/lexsi/llama.cpp/build/bin/llama-server && echo ok'"
  check "$acct: template-check rows present" "$acct 'test -s ~/lexsi/rows/final.jsonl && echo ok'"
done
check "N: env_train has agenttune and auditkit" "N 'ls ~/lexsi/env_train/lib/python3*/site-packages | grep -oE \"^(agenttune|auditkit)-\" | sort -u | wc -l' | grep -qx 2 && echo ok"
check "H: env has agenttune and auditkit" "H 'ls ~/lexsi/env/lib/python3*/site-packages | grep -oE \"^(agenttune|auditkit)-\" | sort -u | wc -l' | grep -qx 2 && echo ok"
A7_N=$(N 'sha256sum ~/lexsi/runs/base_aya-expanse-8b/adapter.gguf | cut -c1-64')
A7_H=$(H 'sha256sum ~/lexsi/runs/base_aya-expanse-8b/adapter.gguf | cut -c1-64')
check "A seed-7 adapter identical on both accounts (${A7_N:0:16})" "[ -n \"$A7_N\" ] && [ \"$A7_N\" = \"$A7_H\" ] && echo ok"
check "H: Stage 1 system files (Tiny Aya bf16, version 1 and 3 adapters)" "H 'test -s ~/lexsi/models/tiny-aya-global-bf16.gguf && test -s ~/lexsi/runs/eval/final_test_trained_adapter.gguf && test -s ~/lexsi/runs/eval/final_test_v3_adapter.gguf && echo ok'"
echo "A seed-7 adapter sha256 (to commit with the frozen configuration): $A7_N"
[ $FAILED = 0 ] && echo "PREFLIGHT PASSED" || { echo "PREFLIGHT FAILED"; exit 1; }
