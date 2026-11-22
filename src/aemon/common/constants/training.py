"""Training settings fixed in code."""

from __future__ import annotations

GATE_FAILED = 3

TARGETS = 'all-linear'  # LoRA on every linear layer, which beats attention-only in published comparisons
# The same layers by name, for Unsloth, which takes no 'all-linear': every linear layer of a block (not lm_head), keyed by
# the checkpoint's model_type. Qwen3.5 adds its linear-attention projections (what 'all-linear' wraps in peft).
UNSLOTH_TARGETS = ('q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj')
UNSLOTH_TARGETS_BY_MODEL_TYPE = {
    'cohere': UNSLOTH_TARGETS,
    'cohere2': UNSLOTH_TARGETS,
    'qwen3_5': (*UNSLOTH_TARGETS, 'in_proj_qkv', 'in_proj_z', 'in_proj_b', 'in_proj_a', 'out_proj'),
}
