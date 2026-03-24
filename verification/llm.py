"""LLM interface for the verification pipeline.

Wraps the same model backends used by mission.sh — Claude CLI and local MLX
models — so verification uses the identical infrastructure as generation.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

GRID_DIR = Path(__file__).resolve().parent.parent
MODELS_CONF = GRID_DIR / ".mission" / "models.conf"


def _read_model_cmd(name: str) -> str | None:
    """Read a model command from models.conf (same logic as mission.sh)."""
    if not MODELS_CONF.exists():
        return None
    for line in MODELS_CONF.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, cmd = line.split("=", 1)
            if key.strip() == name:
                return cmd.strip()
    return None


def call_llm(prompt: str, model: str | None = None) -> str:
    """Call the LLM and return raw text output.

    Uses the same dispatch logic as mission.sh's run_prompt():
    - claude: pipes prompt via stdin to `claude -p`
    - local/ollama: pipes prompt via stdin to the MLX wrapper
    """
    if model is None:
        model = "claude"

    cmd_str = _read_model_cmd(model)
    if cmd_str is None:
        raise RuntimeError(f"Unknown model '{model}' — not found in {MODELS_CONF}")

    if model in ("local", "ollama", "deepseek", "router"):
        # MLX / ollama — pipe prompt via stdin
        proc = subprocess.run(
            cmd_str,
            input=prompt,
            capture_output=True,
            text=True,
            shell=True,
            timeout=300,
            cwd=str(GRID_DIR),
        )
    else:
        # Claude CLI or similar — pipe via stdin
        proc = subprocess.run(
            cmd_str,
            input=prompt,
            capture_output=True,
            text=True,
            shell=True,
            timeout=300,
            cwd=str(GRID_DIR),
        )

    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        raise RuntimeError(
            f"LLM call failed (model={model}, exit={proc.returncode}): {stderr}"
        )

    return proc.stdout.strip()


def call_llm_json(prompt: str, model: str | None = None) -> dict:
    """Call the LLM and parse the response as JSON.

    Handles common cases: JSON in code fences, extra text around JSON, etc.
    """
    raw = call_llm(prompt, model=model)
    return parse_json_response(raw)


def parse_json_response(raw: str) -> dict:
    """Extract and parse JSON from an LLM response.

    Tries: direct parse, fenced block extraction, regex for outermost braces.
    """
    text = raw.strip()

    # Try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return {"items": parsed}
        return parsed
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ``` fences
    fenced = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Find outermost { ... } or [ ... ]
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    start = None

    # Last resort — try to find a JSON array
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "[":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    parsed = json.loads(text[start : i + 1])
                    return {"items": parsed} if isinstance(parsed, list) else parsed
                except json.JSONDecodeError:
                    start = None

    raise ValueError(f"Could not parse JSON from LLM response:\n{text[:500]}")
