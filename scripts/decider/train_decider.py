"""Train the decision head for the evidence kind (DECISIONS, 20 November, registered): LoRA on the base model and a head
that is the LM head's rows for the six option letters, trained by cross-entropy over those six at the answer position.
At step 0 the head is exactly the zero-shot decider, so training only moves it from there.

Usage: python scripts/decider/train_decider.py --model DIR --items train_items.jsonl --calibration calibration_items.jsonl --out DIR
"""

import argparse
import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup

from aemon.agent.decision import KINDS, LETTERS, kind_prompt

log = logging.getLogger('train_decider')
TARGETS = ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']


@dataclass(frozen=True)
class Settings:
    epochs: int = 2
    learning_rate: float = 1e-4
    batch: int = 8
    micro_batch: int = 2
    warmup_share: float = 0.05
    seed: int = 7
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05


def letter_ids(tokenizer: AutoTokenizer) -> list[list[int]]:
    """Token ids that can carry each option letter as the first reply token: the bare letter and the letter after a
    space, whichever are single tokens. The zero-shot reader also strips spaces, so both count as the letter."""
    found = []
    for letter in LETTERS:
        variants = {tuple(tokenizer.encode(text, add_special_tokens=False)) for text in (letter, f' {letter}')}
        ids = sorted({v[0] for v in variants if len(v) == 1})
        if not ids:
            raise ValueError(f'letter {letter} is not a single token')
        found.append(ids)
    return found


def encode(tokenizer: AutoTokenizer, item: dict) -> list[int]:
    prompt = kind_prompt(item['title'], item['origin'] == 'company_claim', item['quote'])
    messages = [{'role': 'user', 'content': prompt}]
    # the rendered template already starts with BOS, as the server's does (template_check)
    text = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    return tokenizer.encode(text, add_special_tokens=False)


def letter_logits(model: torch.nn.Module, batch: list[list[int]], ids: list[list[int]], pad: int) -> torch.Tensor:
    """The six letters' scores at the answer position (left padding, so the last position), each letter the
    log-sum-exp over its token variants."""
    width = max(len(row) for row in batch)
    input_ids = torch.tensor([[pad] * (width - len(row)) + row for row in batch], device=model.device)
    mask = torch.tensor([[0] * (width - len(row)) + [1] * len(row) for row in batch], device=model.device)
    # only the answer position's logits: the full vocabulary at every position does not fit a 40 GB slice
    last = model(input_ids=input_ids, attention_mask=mask, logits_to_keep=1).logits[:, -1, :].float()
    return torch.stack([torch.logsumexp(last[:, variant], dim=-1) for variant in ids], dim=-1)


def evaluate(model: torch.nn.Module, encoded: list[list[int]], golds: list[int], ids: list[list[int]], pad: int) -> dict:
    model.eval()
    losses, correct = [], 0
    with torch.no_grad():
        for start in range(0, len(encoded), 8):
            scores = letter_logits(model, encoded[start : start + 8], ids, pad)
            target = torch.tensor(golds[start : start + 8], device=scores.device)
            losses.append(torch.nn.functional.cross_entropy(scores, target, reduction='sum').item())
            correct += (scores.argmax(-1) == target).sum().item()
    model.train()
    return {'loss': sum(losses) / len(encoded), 'accuracy': correct / len(encoded)}


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def train(model: torch.nn.Module, data: tuple, settings: Settings, ids: list[list[int]], pad: int) -> list[dict]:
    train_x, train_y, cal_x, cal_y = data
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=settings.learning_rate)
    steps = settings.epochs * ((len(train_x) + settings.batch - 1) // settings.batch)
    schedule = get_linear_schedule_with_warmup(optimizer, int(steps * settings.warmup_share), steps)
    history = [{'epoch': 0, 'calibration': evaluate(model, cal_x, cal_y, ids, pad)}]
    log.info('before training %s', history[0])
    order = list(range(len(train_x)))
    rng = random.Random(settings.seed)
    for epoch in range(1, settings.epochs + 1):
        rng.shuffle(order)
        for start in range(0, len(order), settings.batch):
            chosen = order[start : start + settings.batch]
            # the same effective batch, in micro-batches with accumulated gradients (memory)
            for part in range(0, len(chosen), settings.micro_batch):
                micro = chosen[part : part + settings.micro_batch]
                scores = letter_logits(model, [train_x[i] for i in micro], ids, pad)
                target = torch.tensor([train_y[i] for i in micro], device=scores.device)
                loss = torch.nn.functional.cross_entropy(scores, target, reduction='sum') / len(chosen)
                loss.backward()
            optimizer.step()
            schedule.step()
            optimizer.zero_grad()
        history.append({'epoch': epoch, 'calibration': evaluate(model, cal_x, cal_y, ids, pad)})
        log.info('epoch %d %s', epoch, history[-1])
    return history


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--items', type=Path, required=True)
    parser.add_argument('--calibration', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    settings = Settings()
    torch.manual_seed(settings.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    pad = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    ids = letter_ids(tokenizer)
    train_items, cal_items = load(args.items), load(args.calibration)
    data = (
        [encode(tokenizer, i) for i in train_items],
        [KINDS.index(i['gold']) for i in train_items],
        [encode(tokenizer, i) for i in cal_items],
        [KINDS.index(i['gold']) for i in cal_items],
    )
    base = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16, device_map={'': 0})
    lora = LoraConfig(r=settings.rank, lora_alpha=settings.alpha, lora_dropout=settings.dropout, target_modules=TARGETS, task_type='CAUSAL_LM')
    base.gradient_checkpointing_enable()
    base.enable_input_require_grads()
    model = get_peft_model(base, lora)
    history = train(model, data, settings, ids, pad)
    args.out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out / 'adapter')
    report = {'settings': settings.__dict__, 'letter_ids': ids, 'train_items': len(train_items), 'calibration_items': len(cal_items), 'history': history}
    (args.out / 'train_report.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
