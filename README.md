# Grid — Mission Control for Claude Code + Obsidian

Grid is a research and execution harness that orchestrates Claude Code in headless mode, logs everything to an Obsidian vault, and supports a full bidirectional feedback loop.

Write missions as JSON or natural language. Grid breaks them into tasks, runs them through Claude (or other models), validates results, and writes structured Obsidian notes you can annotate. On re-run, your annotations feed back into the prompts.

## Prerequisites

```bash
brew install jq bash    # Bash 4+ required (macOS ships 3.2)
# Install Claude Code: https://docs.anthropic.com/en/docs/claude-code
# Install Obsidian: https://obsidian.md (optional, for the knowledge vault)
```

## Quick Start

```bash
cd ~/Documents/Grid

# Run the example mission
./mission.sh examples/hac-mvp.json

# Generate a mission from natural language
./mission.sh plan 'Build a REST API for managing bookmarks with tags and search'

# Start a research mission
./mission.sh research 'What are the best approaches to real-time anomaly detection in GPU clusters?'

# Check status
./mission.sh status

# Review completed mission
./mission.sh review hac-mvp
```

## Directory Structure

```
~/Documents/Grid/
├── mission.sh                        # Main orchestrator (executable)
├── .mission/
│   ├── state.json                    # Task statuses (created on first run)
│   ├── models.conf                   # Model backend definitions
│   └── logs/                         # Raw output per task
├── knowledge/                        # Obsidian vault root
│   ├── execplans/                    # Write missions here (JSON or markdown)
│   ├── missions/                     # Results auto-populate here
│   │   └── <mission-name>/
│   │       ├── _index.md             # Dashboard with status table
│   │       ├── _feedback.md          # Global steering notes
│   │       ├── <task-id>.md          # Per-task note with findings
│   │       ├── synthesis.md          # Cross-task synthesis
│   │       ├── gap-analysis.md       # What's still unknown
│   │       └── review.md             # Output of review command
│   ├── decision-log.md              # Shared append-only log
│   └── templates/
│       └── execplan-template.md      # Obsidian template for new plans
├── examples/
│   └── hac-mvp.json                  # Example code mission
├── DECISIONS.md                      # Architectural decisions
└── README.md
```

## Commands

### Run a Mission

```bash
./mission.sh <file>
```

Resolution order: exact path > `knowledge/execplans/<arg>` > `knowledge/execplans/<arg>.json` > `examples/<arg>` > `examples/<arg>.json`

```bash
./mission.sh hac-mvp                  # Finds examples/hac-mvp.json
./mission.sh my-plan.json             # Exact path
```

### Plan (Natural Language to Mission)

```bash
./mission.sh plan 'Build a CLI tool that converts markdown to HTML with syntax highlighting'
echo 'detailed description...' | ./mission.sh plan
./mission.sh plan path/to/brief.md
```

Generates 5-15 concrete tasks with IDs, preconditions, prompts, and validation commands. Saves to `knowledge/execplans/` and asks for confirmation before executing.

### Research

```bash
./mission.sh research 'What are the tradeoffs of CXL memory pooling vs traditional NUMA?'
```

Auto-generates a research mission with:
- 3-5 research tasks from different angles (industry reports, technical specs, forums, academic papers)
- A synthesis task combining all findings
- A gap-analysis task identifying unknowns

### Review

```bash
./mission.sh review <mission-name>
```

Reads all completed task outputs and your "My Notes" annotations. Produces a review with:
- What to investigate next
- Untested assumptions
- Strongest/weakest evidence
- Auto-generated follow-up mission

### Status

```bash
./mission.sh status                   # All missions with completion %
./mission.sh status hac-mvp           # Specific mission task list
```

### Models

```bash
./mission.sh models                   # List available models
./mission.sh --model ollama hac-mvp   # Run with specific model
MODEL=deepseek ./mission.sh hac-mvp   # Via environment variable
```

## Writing Missions (JSON Schema)

```json
{
  "name": "Mission Name",
  "description": "What this mission does",
  "tasks": [
    {
      "id": "short-kebab-id",
      "name": "Human-readable name",
      "milestone": "Phase name",
      "type": "code",
      "prompt": "Fully self-contained prompt with ALL context needed",
      "expected": "What success looks like",
      "validation": "shell command that exits 0 on success",
      "preconditions": ["task-id-that-must-finish-first"]
    }
  ]
}
```

### Task Types

| Type | Description |
|------|-------------|
| `code` | Implementation task. Runs prompt, validates with shell command. |
| `research` | Appends web search instructions. Default validation checks output length. |
| `synthesis` | Reads all completed task outputs. Identifies contradictions. Produces unified report. |
| `gap-analysis` | Reads synthesis. Identifies unknowns. Generates follow-up mission JSON. |

### Tips for Good Task Prompts

- **Self-contained**: Each prompt must include ALL file paths, specifications, and context. Don't reference other tasks.
- **Specific validation**: `test -f file.py && pytest tests/test_file.py -v` is better than `test -d src/`.
- **Chain preconditions**: If task B needs task A's output, list A in B's preconditions array.
- **Use milestones**: Group related tasks under milestone names for the dashboard.

## The Obsidian Feedback Loop

This is the core differentiator. Grid doesn't just run tasks — it creates a bidirectional feedback loop:

### Writing Phase (Grid -> Obsidian)

After each task, Grid writes a structured note with YAML frontmatter, findings, and a "My Notes" section at the bottom.

### Reading Phase (Obsidian -> Grid)

On re-run, Grid reads your annotations:

1. **My Notes content**: Anything you write in the "My Notes" section is appended to the task prompt as researcher context.

2. **Global feedback**: Content in `_feedback.md` is prepended to EVERY task prompt in the mission.

3. **Inline directives**:
   - `#redo` — Re-run this task (resets state to pending)
   - `#skip` — Skip this task
   - `#pivot:<new direction>` — Replace the task prompt with new text

### Workflow

1. Run a mission: `./mission.sh my-plan`
2. Open `knowledge/` in Obsidian
3. Read findings in each task note
4. Write observations in "My Notes" sections
5. Add global steering in `_feedback.md`
6. Re-run: `./mission.sh my-plan` (completed tasks skip, your notes feed in)
7. Review: `./mission.sh review my-plan`

## Model Switching

Edit `.mission/models.conf` to add or modify backends:

```
claude=claude -p --output-format text
ollama=ollama run qwen3:14b
deepseek=ollama run deepseek-coder-v2
local-api=curl -s http://localhost:8080/v1/chat/completions -d
```

Resolution order: `--model` flag > `MODEL` env var > `claude` default.

## Resuming Failed Missions

Missions are resumable by design:

- Completed tasks are skipped on re-run
- Failed tasks are re-attempted
- State is saved to `.mission/state.json` on every task completion
- Ctrl+C saves state before exiting

To force a re-run of a specific task, add `#redo` to its "My Notes" section in Obsidian.

To reset an entire mission:

```bash
jq 'del(.["mission-name"])' .mission/state.json > tmp && mv tmp .mission/state.json
```
