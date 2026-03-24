#!/Users/nayak/Documents/Grid/.venv/bin/python3
"""OpenAI runner for Grid — reads prompt from stdin, streams response to stdout."""

import sys
import os

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
    print("Add it to your shell profile: export OPENAI_API_KEY='sk-...'", file=sys.stderr)
    sys.exit(1)

prompt = sys.stdin.read().strip()
if not prompt:
    sys.exit(0)

client = OpenAI(api_key=API_KEY)

try:
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()  # final newline
except Exception as e:
    # Fallback to local model if OpenAI fails (quota, billing, rate limit, etc.)
    print(f"⚠ OpenAI unavailable ({str(e)[:60]}...), falling back to local model", file=sys.stderr)

    # Try to use local model as fallback
    try:
        from pathlib import Path
        import subprocess
        grid_dir = Path(__file__).parent
        local_runner = grid_dir / "mlx-run.py"

        if local_runner.exists():
            result = subprocess.run(
                [sys.executable, str(local_runner), "local"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print(result.stdout, end="")
            else:
                print(f"Local model also failed: {result.stderr}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: Local model runner not found at mlx-run.py", file=sys.stderr)
            sys.exit(1)
    except Exception as fallback_error:
        print(f"Fallback failed: {fallback_error}", file=sys.stderr)
        sys.exit(1)
