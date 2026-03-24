# Grid — AI-Powered Research & Execution Harness

Grid is a task orchestration system that breaks down complex projects into manageable tasks, runs them through Claude or local AI models, validates results, and stores everything in an Obsidian vault for iterative refinement.

**Core idea:** Write a mission once (plan, research goal, code task), Grid executes it through your choice of AI backend (Claude for reasoning + web search, local MLX models for offline compute), saves structured notes, and lets you steer future runs by annotating findings.

## Features

- **Intelligent Routing** — `auto` mode routes simple tasks to fast local MLX models (Qwen3-1.7B), complex reasoning to Claude
- **Terminal UI** — Beautiful live dashboard showing task progress, output, and mission history
- **Bidirectional Feedback Loop** — Annotate findings in Obsidian, re-run missions to incorporate your insights
- **Resumable Missions** — Interrupted? Re-run. Failed tasks retry. Completed tasks skip.
- **Web-Aware Research** — Built-in web search + synthesis for competitive intelligence, market analysis, trend research
- **Flexible Backends** — Claude (web search, strong reasoning), Local MLX (offline, fast), or any API

## Quick Start

### 1. Installation

```bash
# Prerequisites
brew install bash jq                    # Bash 4+, JSON processor

# Clone Grid (you already did this)
cd ~/Documents/Grid
source .venv/bin/activate              # Or set up a venv

# Start the TUI
clu
```

### 2. First Mission

In the TUI, just type:

```
/plan Build a Python CLI tool that converts Markdown to HTML with syntax highlighting
```

Grid will:
- Ask Claude to generate 5-8 concrete tasks
- Show you the plan for review
- Ask Y/N to execute
- Run tasks live in the dashboard
- Save notes to `knowledge/missions/<name>/`

### 3. Quick Research

```
/research What are the best open-source alternatives to Docker for containerization?
```

Grid generates a research mission with 3-5 research tasks, synthesis, and gap analysis. Everything is cited.

### 4. Simple Questions

```
what is the difference between polymorphism and inheritance?
```

Runs as a quick ask (saved to `knowledge/asks/`), uses auto-routing.

## Terminal UI (TUI)

The TUI is your control center:

```
┌────────────────────────────────────────────────────────────────────────┐
│ ◆ Grid Mission Control    TIME 2m47s   Tasks 3/8   Model auto        │
├────────────────────────────────────────────────────────────────────────┤
│ Active Task                          │ Tasks                          │
│                                      │ ✓ Task 1: Setup               │
│ ▸ Research CXL Vendors               │ ◆ Task 2: Running...          │
│ Searching for post-silicon debug... │ ○ Task 3: Pending             │
│ Found 12 sources from 2025-2026      │ ✗ Task 4: Failed              │
│                                      │                               │
│ ─────────────────────────────────────┼────────────────────────────── │
│ [Output log scrolls here]             │ history                      │
│                                       │ 23:15:22 grid: Planning...   │
│                                       │ 23:15:44 task-1: started ▶   │
│                                       │ 23:16:02 task-1: done ✓      │
└────────────────────────────────────────────────────────────────────────┘
Type prompt and press Ctrl+J to send · m model · s status · r retry · q quit
```

**Keyboard shortcuts:**
- `m` — Switch model (auto / local / claude)
- `s` — Show mission status
- `r` — Mark failed tasks for retry
- `q` — Quit

## Models

Grid comes with three model backends:

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **auto** (default) | Fast | Free | Automatically routes tasks: simple ones to local MLX, complex to Claude |
| **local** | Very Fast | Free | Offline, always-on. Qwen3-14B via MLX (GPU accelerated on M-series Mac) |
| **claude** | Moderate | API $ | Web search, reasoning-heavy tasks, business analysis |

Switch models in the TUI by pressing `m`, or specify via CLI:

```bash
./mission.sh --model local plan "your task"
./mission.sh --model claude research "market opportunity"
MODEL=auto clu                    # Via environment variable
```

## Directory Structure

```
~/Documents/Grid/
├── mission-tui.py               # Terminal UI (run this for dashboard)
├── mission.sh                   # Mission executor
├── mlx-run.py                   # Local MLX model wrapper
├── .mission/
│   ├── models.conf              # Backend definitions (claude, local, router)
│   ├── state.json               # Task statuses (auto-created)
│   └── logs/                    # Raw task output
├── knowledge/                   # Obsidian vault (point vault here)
│   ├── missions/                # Results auto-populate here
│   │   └── <mission-name>/
│   │       ├── _index.md        # Dashboard with status table
│   │       ├── _feedback.md     # Global steering notes (read on re-run)
│   │       ├── <task-id>.md     # Per-task findings + "My Notes" section
│   │       └── synthesis.md     # Cross-task synthesis
│   ├── asks/                    # Quick ask outputs
│   ├── execplans/               # Mission JSON files you write
│   └── decision-log.md          # Append-only log of all decisions
├── examples/
│   └── hac-mvp.json             # Example: 6-task hardware anomaly collection platform
└── README.md
```

## The Feedback Loop (Core Feature)

Grid's killer feature is the **bidirectional feedback loop**. Here's how it works:

### Run 1: Initial Mission

```bash
clu
# Type: /plan Analyze our business plan for risks and feasibility
# Grid generates tasks → runs them → saves notes to knowledge/missions/
```

Each task gets a note with YAML metadata, findings, and a blank "My Notes" section.

### Edit in Obsidian

Open `knowledge/missions/<name>/<task-id>.md`:

```markdown
---
date: 2026-03-23
model: claude
status: completed
---

## Task: Competitive Landscape Analysis

## Findings
Found 12 companies with AI-assisted debug tooling:
- Company A: Announced Q4 2025
- Company B: Shipping now, $50K/seat
- ...

## My Notes
Actually, Company C launched in stealth mode last month. Check CrunchBase. Also the pricing model is per-node, not per-seat, which changes our TAM calculation significantly.

#pivot: include per-node vs per-seat pricing models in future research
```

### Run 2: Re-run with Your Feedback

```bash
clu
# Type: missions/my-business-analysis (auto-completes)
```

Grid will:
1. **Skip completed tasks** (save time)
2. **Re-run flagged tasks**: tasks with `#redo` or `#pivot:new direction`
3. **Feed your notes back in**: "Your notes from the researcher say..." prepended to the task prompt
4. **Use global feedback**: Anything in `_feedback.md` is prepended to EVERY task

So Claude sees your insights and refines based on them.

## Mission JSON Schema

If you want to write missions directly:

```json
{
  "name": "my-business-analysis",
  "description": "Stress-test our business plan for risks, market timing, and product-market fit",
  "tasks": [
    {
      "id": "riskiest-assumptions",
      "name": "Identify Top 5 Riskiest Assumptions",
      "milestone": "Feasibility Validation",
      "type": "research",
      "prompt": "Identify the 5 riskiest assumptions in our business plan...",
      "expected": "A ranked list with evidence and mitigation strategies",
      "validation": "test -s output.md && wc -w output.md | awk '{exit $1 > 500 ? 0 : 1}'",
      "preconditions": []
    },
    {
      "id": "competitive-landscape",
      "name": "Research Competitive Landscape",
      "milestone": "Market Need Validation",
      "type": "research",
      "prompt": "Research who has shipped AI-assisted post-silicon debug tooling...",
      "expected": "5+ named companies with product status, pricing, target customers",
      "validation": "grep -q 'company\\|product' output.md",
      "preconditions": []
    },
    {
      "id": "synthesis",
      "name": "Synthesize All Findings",
      "milestone": "Plan Reconstruction",
      "type": "synthesis",
      "prompt": "Read all completed tasks and identify the single highest-leverage change...",
      "expected": "One-page executive briefing with decision: what to do this week",
      "validation": "wc -l output.md | awk '{exit $1 > 20 ? 0 : 1}'",
      "preconditions": ["riskiest-assumptions", "competitive-landscape"]
    }
  ]
}
```

### Task Types

| Type | Use Case | Validation |
|------|----------|-----------|
| `code` | Write code, scripts, configs | Custom shell command |
| `research` | Find info, analyze sources | Output length check |
| `synthesis` | Combine task outputs | Reads all tasks, custom validation |
| `gap-analysis` | Identify unknowns | Reads synthesis, generates follow-up mission |

## Commands Reference

```bash
clu                                    # Launch the TUI
clu "what is X?"                       # Quick ask (no TUI)
clu plan "Build a feature"             # Generate and run a mission
clu research "Market opportunity"      # Auto-generate research mission
clu status                             # Show all missions
clu status my-mission                  # Show tasks for specific mission
```

Inside the TUI:
```
just type                              # Quick ask
/plan describe what to build           # Generate mission
/research what you want to know        # Generate research mission
```

## Workflow Example

**Scenario:** You're validating a new business idea and need to stress-test your assumptions.

```bash
clu
# Type: /plan "Fourier is an AI-powered post-silicon debug platform for CXL device vendors. Is this viable? What are the biggest risks?"
# Grid: "I'll generate 8 tasks for you. Review? [y/N]"
# You: y

# Tasks run live in dashboard. You see output streaming.
# Grid saves to knowledge/missions/fourier-ai-debug-validation/

# Later, open Obsidian and read the tasks:
# - Task 1: Identified market size, pricing, customer acquisition as biggest unknowns
# - Task 2: Found 3 competing startups and 2 incumbent moves into this space
# - Task 3: Found customer pain points via forums and CXL summit talks

# In "My Notes" sections, you add:
# - "Task 1: Actually, the market is smaller than Claude estimated. CXL adoption is slower in 2026."
# - "Task 2: Competitor X just raised $50M. Add this to the threat landscape."

# Back in TUI:
clu missions/fourier-ai-debug-validation

# Grid re-runs the tasks, but this time:
# - Completed tasks skip
# - Your notes are fed back in: "The researcher noted that CXL adoption is slower..."
# - Output reflects your corrections

clu status missions/fourier-ai-debug-validation
# Shows: 8/8 tasks completed with your feedback integrated
```

## Obsidian Setup

Point your Obsidian vault to `~/Documents/Grid/knowledge/`:

1. Open Obsidian → Vault Switcher (bottom left)
2. "Open folder as vault"
3. Navigate to `~/Documents/Grid/knowledge`
4. Enable graph view to see task relationships

Now Grid's output appears live in your vault.

## Advanced: Custom Models

Edit `.mission/models.conf` to add new backends:

```bash
# Use any API-compatible endpoint
my-local-api=curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"'"$prompt"'"}]}'
```

Then:

```bash
./mission.sh --model my-local-api plan "your task"
```

## Troubleshooting

**"Unknown model" error:**
```bash
./mission.sh models    # List available models
```

**TUI not starting:**
```bash
source ~/.zshrc        # Reload shell
clu                    # Try again
```

**Tasks failing validation:**
1. Check `.mission/logs/<task-id>.log` for raw output
2. Add `#redo` to task's "My Notes" in Obsidian
3. Re-run mission

**Rate-limited by Claude:**
```bash
./mission.sh --model local plan "your task"   # Use local model instead
```

## Architecture

Grid is:
- **Mission orchestrator** (mission.sh) — Validates tasks, manages state, calls model backends
- **Terminal UI** (mission-tui.py) — Live dashboard, task runner, model switcher
- **Local model wrapper** (mlx-run.py) — Qwen3 via MLX for GPU-accelerated inference
- **Knowledge vault** (knowledge/) — Obsidian integration point for the feedback loop

The feedback loop is implemented via:
1. **Writer**: Tasks write to `.md` files with YAML frontmatter and "My Notes" section
2. **Reader**: On re-run, Grid parses `My Notes` and `_feedback.md`, appends to task prompts
3. **Router**: Auto mode intelligently picks local vs Claude based on task complexity

## License

MIT. Fork and extend for your use case.

## Next Steps

1. `clu` to launch the TUI
2. Type `/plan something you want to accomplish`
3. Review the generated mission
4. Watch it execute live
5. Open `knowledge/missions/` in Obsidian to see results
6. Annotate findings with your own insights
7. Re-run to incorporate feedback

Happy researching and building!
