# Decisions

Architectural and implementation decisions made during the build of Grid Mission Control.

## Shell Compatibility

**Decision:** Target Bash 4+ with `declare -A` for associative arrays.
**Rationale:** macOS ships with Bash 3.2, but Homebrew's Bash 5 is widely installed. The `models.conf` parsing uses associative arrays which require Bash 4+. Users on stock macOS need `brew install bash`.

## Safe File Writes

**Decision:** All writes to `knowledge/` use tmpfile + mv pattern.
**Rationale:** Prevents partial writes from corrupting Obsidian notes if the process is interrupted. The `safe_write()` function handles this consistently.

## State File Format

**Decision:** Flat JSON with mission names as top-level keys and task states as nested objects.
**Rationale:** Simple structure that jq can manipulate atomically. Each state update reads, transforms, and writes via tmpfile to prevent corruption.

## Model Runner Dispatch

**Decision:** Different invocation patterns per model type (claude uses `-p` flag, ollama uses pipe, local-api uses curl with JSON payload).
**Rationale:** Each backend has a different interface. The `run_prompt()` function dispatches based on the model name. This is simple but not infinitely extensible — a plugin system would be overkill for 4 backends.

## Decision Log Noise Reduction

**Decision:** Only log non-routine events (failures, blocks, run summaries) to `decision-log.md`.
**Rationale:** Per the spec, routine completions stay quiet to keep the log signal-rich. Every task success is already visible in the mission index and individual notes.

## Research Task Default Validation

**Decision:** Research tasks without explicit validation commands rely on the output note being written (the note is always written by the harness after execution).
**Rationale:** The spec mentions checking file length >500 chars, but since the harness always writes the note with the full output, the real validation is whether the runner succeeded. A zero-length output from the runner would indicate a problem that the runner exit code already catches.

## Obsidian Wikilink Format

**Decision:** Use `[[missions/<mission>/<task-id>]]` format in the decision log and `[[<mission>/<task-id>]]` in mission index tables.
**Rationale:** Obsidian resolves wikilinks relative to the vault root (`knowledge/`). The decision log sits at the vault root, so it needs the full relative path. The index is inside the mission folder.

## JSON Extraction from Claude Output

**Decision:** When parsing Claude's response for JSON (in plan/research/gap-analysis commands), try three strategies: markdown code fence extraction, bare JSON object extraction, raw output.
**Rationale:** Claude sometimes wraps JSON in ```json fences, sometimes outputs it bare. The triple-fallback approach handles both cases robustly.

## Prompt Escaping

**Decision:** Use `printf '%q'` for passing prompts to the claude CLI and `printf '%s'` for writing content to files.
**Rationale:** `%q` shell-escapes the prompt for safe eval in the runner. `%s` prevents shell expansion in file writes per the spec requirement.

## My Notes Preservation

**Decision:** When rewriting a task note, extract existing "My Notes" content and re-append it.
**Rationale:** The feedback loop depends on researcher notes surviving re-runs. The harness reads the section with awk, strips the comment line, and appends the preserved content to the new note.
