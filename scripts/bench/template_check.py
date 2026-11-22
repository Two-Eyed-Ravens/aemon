"""Does the server feed the model the same tokens training did? For one training row's context, compares the tokens
llama-server builds for a chat request (its --jinja template, then tokenization with special tokens added, as the chat
endpoint does) with the tokens training used (the Hugging Face chat template with the generation prompt, tokenized
without adding special tokens; src/aemon/rows/build_rows.py labels_for). A difference, such as a doubled BOS token or
other role markers, means the evaluation would not test the model as trained. Exits 1 on a difference.

Usage: python template_check.py --url http://127.0.0.1:PORT --tokenizer HF_DIR --rows final.jsonl
"""

import argparse
import json
import sys
import urllib.request

from transformers import AutoTokenizer


def post(url: str, body: dict) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--tokenizer', required=True)
    parser.add_argument('--rows', required=True)
    args = parser.parse_args()
    with open(args.rows) as handle:
        row = json.loads(handle.readline())
    context = row['messages'][: row['target_index']]
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    text = tokenizer.apply_chat_template(context, tokenize=False, add_generation_prompt=True)
    trained = tokenizer(text, add_special_tokens=False)['input_ids']
    prompt = post(args.url + '/apply-template', {'messages': context})['prompt']
    served = post(args.url + '/tokenize', {'content': prompt, 'add_special': True, 'parse_special': True})['tokens']
    same = list(trained) == list(served)
    print(
        json.dumps(
            {
                'same_tokens': same,
                'trained': len(trained),
                'served': len(served),
                'trained_head': trained[:6],
                'served_head': served[:6],
                'trained_tail': trained[-6:],
                'served_tail': served[-6:],
            }
        )
    )
    if not same:
        sys.exit(1)


if __name__ == '__main__':
    main()
