#!/usr/bin/env python3
"""MLX agent with file tool-use loop for Grid.

Gives local Qwen3 models the ability to read, write, list, and delete
files by running a multi-turn tool-calling loop.

Usage:
    echo "prompt" | mlx-agent.py [model-key]
    mlx-agent.py [model-key] "prompt text"

Model keys:
    local      - Qwen3-14B-4bit  (default)
    local-8b   - Qwen3-8B-4bit
    local-32b  - Qwen3-32B-4bit  (needs memory optimizations on 24GB)
"""
import sys
import os
import json
import re
import select
import glob as glob_mod

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

MODELS = {
    "local":      "mlx-community/Qwen3-14B-4bit",
    "local-8b":   "mlx-community/Qwen3-8B-4bit",
    "local-32b":  "mlx-community/Qwen3-32B-4bit",
}

# Models that need memory optimizations (KV cache quantization, capped context)
LARGE_MODELS = {"local-32b"}

MAX_TOOL_ROUNDS = 8
MAX_TOKENS_TOOL = 2048
MAX_TOKENS_FINAL = 4096

# ─── Tool definitions (Qwen function-calling format) ────────────────────────
# Full toolset for models with headroom
TOOLS = [
    {"type": "function", "function": {
        "name": "list_directory",
        "description": "List files in a directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."},
            "recursive": {"type": "boolean", "description": "List 2 levels deep. Default false."}
        }, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file's text content.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."},
            "max_lines": {"type": "integer", "description": "Max lines. Default 200."}
        }, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write content to a file. Creates dirs if needed.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."},
            "content": {"type": "string", "description": "Content to write."}
        }, "required": ["path", "content"]}
    }},
    {"type": "function", "function": {
        "name": "delete_file",
        "description": "Delete a file or empty directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."}
        }, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "search_files",
        "description": "Search for files by glob pattern or text content.",
        "parameters": {"type": "object", "properties": {
            "directory": {"type": "string", "description": "Dir to search."},
            "pattern": {"type": "string", "description": "Glob pattern, e.g. '*.md'"},
            "text": {"type": "string", "description": "Text to find in files."}
        }, "required": ["directory"]}
    }},
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run a shell command, return stdout.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "Shell command."}
        }, "required": ["command"]}
    }}
]

# Minimal toolset for memory-constrained large models (fewer tokens in prompt)
TOOLS_MINIMAL = [
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write content to a file. Creates dirs if needed.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."},
            "content": {"type": "string", "description": "Content to write."}
        }, "required": ["path", "content"]}
    }},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file's text content.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Absolute path."}
        }, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run a shell command, return stdout.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "Shell command."}
        }, "required": ["command"]}
    }}
]

# ─── Tool execution ──────────────────────────────────────────────────────────

def expand_path(p):
    return os.path.expandvars(os.path.expanduser(p))


def _human_size(nbytes):
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.0f}{unit}"
        nbytes /= 1024
    return f"{nbytes:.1f}TB"


def exec_tool(name, args):
    try:
        if name == "list_directory":
            path = expand_path(args.get("path", "."))
            recursive = args.get("recursive", False)
            if not os.path.isdir(path):
                return f"Error: '{path}' is not a directory"
            entries = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    depth = root.replace(path, "").count(os.sep)
                    if depth >= 2:
                        dirs.clear()
                        continue
                    for f in files[:50]:
                        fp = os.path.join(root, f)
                        try:
                            sz = os.path.getsize(fp)
                            entries.append(f"  {os.path.relpath(fp, path)}  ({_human_size(sz)})")
                        except OSError:
                            entries.append(f"  {os.path.relpath(fp, path)}")
                    for d in dirs[:20]:
                        entries.append(f"  {os.path.relpath(os.path.join(root, d), path)}/")
                    if len(entries) > 100:
                        entries.append("  ... (truncated)")
                        break
            else:
                for item in sorted(os.listdir(path))[:80]:
                    fp = os.path.join(path, item)
                    if os.path.isdir(fp):
                        entries.append(f"  {item}/")
                    else:
                        try:
                            sz = os.path.getsize(fp)
                            entries.append(f"  {item}  ({_human_size(sz)})")
                        except OSError:
                            entries.append(f"  {item}")
            return f"Contents of {path}:\n" + "\n".join(entries) if entries else f"{path} is empty"

        elif name == "read_file":
            path = expand_path(args.get("path", ""))
            max_lines = args.get("max_lines", 200)
            if not os.path.isfile(path):
                return f"Error: '{path}' not found"
            with open(path, "r", errors="replace") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... (truncated at {max_lines} lines)")
                        break
                    lines.append(line)
            return "".join(lines)

        elif name == "write_file":
            path = expand_path(args.get("path", ""))
            content = args.get("content", "")
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Written {len(content)} bytes to {path}"

        elif name == "delete_file":
            path = expand_path(args.get("path", ""))
            if os.path.isfile(path):
                os.remove(path)
                return f"Deleted file: {path}"
            elif os.path.isdir(path):
                if len(os.listdir(path)) == 0:
                    os.rmdir(path)
                    return f"Deleted empty directory: {path}"
                else:
                    return f"Error: directory '{path}' is not empty. Won't delete non-empty directories for safety."
            else:
                return f"Error: '{path}' not found"

        elif name == "search_files":
            directory = expand_path(args.get("directory", "."))
            pattern = args.get("pattern", "*")
            text = args.get("text", "")
            matches = []
            for fp in glob_mod.glob(os.path.join(directory, "**", pattern), recursive=True):
                if os.path.isfile(fp):
                    if text:
                        try:
                            with open(fp, "r", errors="replace") as f:
                                content = f.read(50000)
                            if text.lower() in content.lower():
                                matches.append(fp)
                        except Exception:
                            pass
                    else:
                        matches.append(fp)
                if len(matches) >= 30:
                    break
            if matches:
                return f"Found {len(matches)} matches:\n" + "\n".join(f"  {m}" for m in matches)
            return "No matches found"

        elif name == "run_command":
            import subprocess
            cmd = args.get("command", "")
            dangerous = ["rm -rf /", "rm -rf ~", "sudo", "mkfs", "dd if=", "> /dev/"]
            for d in dangerous:
                if d in cmd:
                    return f"Error: blocked dangerous command pattern '{d}'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]: " + result.stderr
            return output[:5000] if output else "(no output)"

        else:
            return f"Error: unknown tool '{name}'"

    except Exception as e:
        return f"Error: {e}"


# ─── Parse tool calls from model output ─────────────────────────────────────

def parse_tool_calls(text):
    calls = []

    # Try closed <tool_call>...</tool_call> tags first
    for match in re.finditer(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', text, re.DOTALL):
        try:
            data = json.loads(match.group(1), strict=False)
            name = data.get("name", "")
            arguments = data.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            calls.append({"name": name, "arguments": arguments})
        except json.JSONDecodeError:
            continue

    # Fallback: unclosed <tool_call> tag (common when generation hits token limit)
    # Handles both: <tool_call>\n{"name":"x","arguments":{...}}
    #           and: <tool_call> tool_name\n{args...}
    if not calls:
        for match in re.finditer(r'<tool_call>\s*(\w+)?\s*(\{.*)', text, re.DOTALL):
            inline_name = match.group(1) or ""
            raw = match.group(2).strip()
            # Try to find valid JSON by progressively trimming from the end
            for end in range(len(raw), 0, -1):
                try:
                    data = json.loads(raw[:end], strict=False)
                    # JSON may have "name" key, or name may be inline after <tool_call>
                    name = data.get("name", "") or inline_name
                    arguments = data.get("arguments", {})
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    # If no "arguments" key, the whole JSON IS the arguments
                    if not arguments and "name" not in data and name:
                        arguments = data
                    if name:
                        calls.append({"name": name, "arguments": arguments})
                    break
                except json.JSONDecodeError:
                    continue

    # Fallback: function_call format
    if not calls:
        for match in re.finditer(r'\{[^{}]*"function_call"[^{}]*\{[^}]*\}[^}]*\}', text):
            try:
                data = json.loads(match.group(), strict=False)
                fc = data.get("function_call", {})
                calls.append({"name": fc.get("name", ""), "arguments": fc.get("arguments", {})})
            except json.JSONDecodeError:
                continue

    # Fallback: CLI-style <tool_call> tool_name --arg value --arg "value"
    if not calls:
        for match in re.finditer(r'<tool_call>\s*(\w+)\s+--(\w+)\s+(.*?)(?:</tool_call>|\Z)', text, re.DOTALL):
            tool_name = match.group(1)
            rest = "--" + match.group(2) + " " + match.group(3)
            args = {}
            # Parse --key value or --key "multiline value" pairs
            for kv in re.finditer(r'--(\w+)\s+(?:"((?:[^"\\]|\\.)*)"|(\S+))', rest, re.DOTALL):
                key = kv.group(1)
                val = kv.group(2) if kv.group(2) is not None else kv.group(3)
                args[key] = val
            if tool_name and args:
                calls.append({"name": tool_name, "arguments": args})

    return calls


def strip_thinking(text):
    return re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL).strip()


# ─── Main agent loop ─────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    # First arg may be a model key
    model_key = "local"
    if args and args[0] in MODELS:
        model_key = args.pop(0)

    model_path = MODELS[model_key]

    # Remaining args are the prompt, or read from stdin
    prompt = None
    if args:
        prompt = " ".join(args)
    if prompt is None:
        if select.select([sys.stdin], [], [], 10.0)[0]:
            prompt = sys.stdin.read().strip()
    if not prompt:
        print("Error: no prompt provided", file=sys.stderr)
        sys.exit(1)

    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_logits_processors, make_sampler
    import mlx.core as mx

    # For large models: set tight memory limits before loading
    if model_key in LARGE_MODELS:
        mx.set_cache_limit(0)  # Release GPU cache immediately — no buffer reuse

    model, tokenizer = load(model_path)

    if model_key in LARGE_MODELS:
        mx.clear_cache()  # Free any temp buffers from loading

    # Repetition penalty to prevent degenerate looping
    logits_processors = make_logits_processors(
        repetition_penalty=1.2,
        repetition_context_size=100,
    )
    # Lower temp for large quantized models to keep output coherent
    temp = 0.4 if model_key in LARGE_MODELS else 0.7
    sampler = make_sampler(temp=temp, top_p=0.9, min_p=0.05)

    # Memory optimization kwargs for large models on 24GB
    # NOTE: max_kv_size (RotatingKVCache) and kv_bits can't be combined in mlx-lm 0.31.x
    gen_kwargs = {}
    if model_key in LARGE_MODELS:
        gen_kwargs.update(
            max_kv_size=1536,        # Cap KV cache tightly for 24GB systems
            prefill_step_size=256,   # Smaller prefill chunks to avoid OOM spikes
        )

    work_dir = os.getcwd()
    docs_dir = work_dir + "/knowledge/docs"

    # For large models: skip the Qwen tool template (saves ~2k tokens) and
    # embed tool-calling instructions directly in the system prompt instead
    is_large = model_key in LARGE_MODELS

    if is_large:
        system_msg = (
            "You are Grid, a coding assistant. You TAKE ACTION by calling tools.\n"
            "Save files to: " + docs_dir + "\n"
            "Home dir: " + os.path.expanduser("~") + "\n\n"
            "To call a tool, output exactly this format:\n"
            '<tool_call>\n{"name": "write_file", "arguments": {"path": "/abs/path", "content": "file contents"}}\n</tool_call>\n\n'
            "Available tools: write_file, read_file, run_command.\n"
            "RULES: When asked to create a script, IMMEDIATELY output a <tool_call> for write_file with the complete code. "
            "Do NOT explain or plan first. Use absolute paths. Be brief after the tool runs."
        )
    else:
        system_msg = (
            "You are Grid, a coding assistant that TAKES ACTION using tools. "
            "You have access to the user's local filesystem via tools: "
            "write_file, read_file, list_directory, search_files, run_command, delete_file.\n\n"
            "CRITICAL RULES:\n"
            "- When the user asks you to write or create something, you MUST use the write_file tool to create the file. "
            "Do NOT just describe what you would do — actually do it.\n"
            "- When asked to create a script, write complete working code using write_file. "
            "Save scripts and generated files to: " + docs_dir + "\n"
            "- Always use absolute paths. The user's home directory is: " + os.path.expanduser("~") + "\n"
            "- When you need information about existing files, use read_file or list_directory — don't guess.\n"
            "- Keep your text responses brief. Let the code speak for itself.\n"
            "- After writing a file, confirm what you wrote and where."
        )

    tools = TOOLS_MINIMAL if is_large else TOOLS
    max_tool_tokens = 1536 if is_large else MAX_TOKENS_TOOL
    max_final_tokens = 2048 if is_large else MAX_TOKENS_FINAL

    # Disable thinking for large models to save KV cache memory
    user_prompt = prompt + " /no_think" if is_large else prompt

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ]

    for round_num in range(MAX_TOOL_ROUNDS):
        if is_large:
            mx.clear_cache()  # Reclaim memory between rounds

        # Large models: no tool template (saves tokens), tools described in system prompt
        chat_prompt = tokenizer.apply_chat_template(
            messages,
            tools=None if is_large else tools,
            tokenize=False,
            add_generation_prompt=True,
        )

        response = generate(
            model, tokenizer,
            prompt=chat_prompt,
            max_tokens=max_tool_tokens if round_num < MAX_TOOL_ROUNDS - 1 else max_final_tokens,
            verbose=False,
            sampler=sampler,
            logits_processors=logits_processors,
            **gen_kwargs,
        )

        clean = strip_thinking(response)
        tool_calls = parse_tool_calls(clean)

        if not tool_calls:
            final = re.sub(r'<tool_call>.*?</tool_call>', '', clean, flags=re.DOTALL).strip()
            print(final)
            return

        messages.append({"role": "assistant", "content": response})

        wrote_file = False
        for tc in tool_calls:
            tool_name = tc["name"]
            tool_args = tc["arguments"]
            print(f"  [tool: {tool_name}({json.dumps(tool_args, ensure_ascii=False)[:80]})]", file=sys.stderr)
            result = exec_tool(tool_name, tool_args)
            if tool_name == "write_file":
                wrote_file = True
            if is_large:
                # Without Qwen tool template, format results as user messages
                messages.append({
                    "role": "user",
                    "content": f"[Tool result for {tool_name}]: {result[:1000]}"
                })
            else:
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

        # For large models: after a successful write_file, print confirmation and exit
        # rather than risking OOM on the summary generation round
        if is_large and wrote_file:
            for tc in tool_calls:
                if tc["name"] == "write_file":
                    path = tc["arguments"].get("path", "")
                    print(f"Created: {path}")
            return

    # Exhausted rounds — ask for summary
    print("(Agent reached max tool rounds)", file=sys.stderr)
    chat_prompt = tokenizer.apply_chat_template(
        messages + [{"role": "user", "content": "Please summarize your findings now."}],
        tools=None if is_large else tools,
        tokenize=False,
        add_generation_prompt=True,
    )
    response = generate(model, tokenizer, prompt=chat_prompt, max_tokens=max_final_tokens, verbose=False, sampler=sampler, logits_processors=logits_processors, **gen_kwargs)
    print(strip_thinking(response))


if __name__ == "__main__":
    main()
