#!/usr/bin/env python3
"""MLX inference wrapper for Grid mission.sh.

Usage:
    echo "prompt" | mlx-run.py [model-name]
    mlx-run.py [model-name] "prompt text"

Models:
    router  - Qwen3-1.7B-4bit (fast, for task routing)
    local   - Qwen3-14B-4bit  (capable, for reasoning tasks)
"""
import sys
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

MODELS = {
    "router":   "mlx-community/Qwen3-1.7B-4bit",
    "local":    "mlx-community/Qwen3-14B-4bit",
    "local-8b": "mlx-community/Qwen3-8B-4bit",
}

def main():
    model_name = "local"
    prompt = None

    args = sys.argv[1:]
    if args and args[0] in MODELS:
        model_name = args.pop(0)
    if args:
        prompt = " ".join(args)

    if prompt is None:
        import select
        if select.select([sys.stdin], [], [], 5.0)[0]:
            prompt = sys.stdin.read().strip()
        else:
            print("Error: no prompt provided via stdin or arguments", file=sys.stderr)
            sys.exit(1)

    if not prompt:
        print("Error: empty prompt", file=sys.stderr)
        sys.exit(1)

    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_logits_processors, make_sampler

    model_path = MODELS[model_name]
    model, tokenizer = load(model_path)

    # Repetition penalty to prevent degenerate looping
    logits_processors = make_logits_processors(
        repetition_penalty=1.2,
        repetition_context_size=100,
    )
    sampler = make_sampler(temp=0.7, top_p=0.9)

    if model_name == "router":
        max_tokens = 150
        # Use chat template with thinking disabled for fast routing
        messages = [{"role": "user", "content": prompt + " /no_think"}]
    else:
        max_tokens = 4096
        messages = [{"role": "user", "content": prompt}]

    # Apply chat template
    chat_prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    response = generate(
        model, tokenizer,
        prompt=chat_prompt,
        max_tokens=max_tokens,
        verbose=False,
        sampler=sampler,
        logits_processors=logits_processors,
    )

    # Strip any thinking tags from output
    output = response
    if "<think>" in output:
        # Remove thinking block
        import re
        output = re.sub(r'<think>.*?</think>\s*', '', output, flags=re.DOTALL)

    print(output.strip())

if __name__ == "__main__":
    main()
