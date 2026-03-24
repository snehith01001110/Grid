#!/Users/nayak/Documents/Grid/.venv/bin/python3
"""Grid Mission Control — Terminal UI v3"""

import sys
import os
import json
import subprocess
import threading
import time
import re
from pathlib import Path
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog, Input, Label, TextArea
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive
from textual import work
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.message import Message
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

GRID_DIR = Path(__file__).parent
STATE_FILE = GRID_DIR / ".mission" / "state.json"
LOGS_DIR = GRID_DIR / ".mission" / "logs"
KNOWLEDGE_DIR = GRID_DIR / "knowledge"
MISSION_SH = GRID_DIR / "mission.sh"
MODELS_CONF = GRID_DIR / ".mission" / "models.conf"

ANSI = re.compile(r'\x1b\[[0-9;]*m')

# ── Theme ────────────────────────────────────────────────────────────────────
BG_DARK = "#0c0c0c"
BG_PANEL = "#141414"
BG_INPUT = "#1a1a1a"
BG_STATSBAR = "#1a1a1a"
BORDER = "#2a2a2a"
BORDER_FOCUS = "#e07020"

ORANGE = "#e07020"
AMBER = "#d4a030"
GREEN = "#3dba6e"
RED = "#e04848"
PENDING_GRAY = "#555555"
WHITE = "#d0d0d0"
DIM = "#606060"
DIMMER = "#404040"
CYAN = "#50b4c8"
TEAL = "#40a89a"

MEMORY_FILE = GRID_DIR / "knowledge" / "grid-memory.md"

SPINNER_FRAMES = ["◐", "◑", "◒", "◓"]

STATUS_ICON = {
    "completed": ("✓", GREEN),
    "failed": ("✗", RED),
    "running": ("◐", AMBER),
    "skipped": ("⊘", PENDING_GRAY),
    "pending": ("·", PENDING_GRAY),
    "blocked": ("⏸", PENDING_GRAY),
}


def read_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def elapsed_str(start):
    s = int(time.time() - start)
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m{s % 60:02d}s"


def strip_ansi(s):
    return ANSI.sub('', s)


def read_models():
    """Read user-selectable models from models.conf (skip internal ones like router)."""
    INTERNAL = {"router"}
    models = {}
    try:
        for line in MODELS_CONF.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                name, cmd = line.split('=', 1)
                name = name.strip()
                if name not in INTERNAL:
                    models[name] = cmd.strip()
    except Exception:
        pass
    return models


def selectable_models():
    """Return ordered list: auto first, then configured models."""
    return ["auto"] + list(read_models().keys())


def read_mission_json(arg):
    candidates = [
        Path(arg),
        KNOWLEDGE_DIR / "execplans" / arg,
        KNOWLEDGE_DIR / "execplans" / f"{arg}.json",
        GRID_DIR / "examples" / arg,
        GRID_DIR / "examples" / f"{arg}.json",
    ]
    for c in candidates:
        if c.exists():
            try:
                return json.loads(c.read_text())
            except Exception:
                return None
    return None


def list_missions():
    """List recent missions from state.json."""
    state = read_state()
    missions = []
    for name, tasks in state.items():
        done = sum(1 for v in tasks.values() if v == "completed")
        fail = sum(1 for v in tasks.values() if v == "failed")
        total = len(tasks)
        missions.append((name, done, fail, total))
    return missions


# ── Model Selector Screen ────────────────────────────────────────────────────

class ModelSelector(ModalScreen):
    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select_model", "Select", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    CSS = f"""
    ModelSelector {{
        align: center middle;
    }}
    #model-dialog {{
        width: 44;
        height: auto;
        max-height: 16;
        background: {BG_PANEL};
        border: solid {ORANGE};
        padding: 1 2;
    }}
    """

    def __init__(self, current_model: str):
        super().__init__()
        self.current = current_model
        self._models = selectable_models()
        self._cursor = self._models.index(current_model) if current_model in self._models else 0

    def compose(self) -> ComposeResult:
        with Vertical(id="model-dialog"):
            yield Static(id="model-list")
            yield Static(Text("↑↓ navigate · Enter select · Esc cancel", style=DIM))

    def on_mount(self):
        self._render_list()

    def _render_list(self):
        t = Text()
        t.append(" SELECT MODEL\n", style=f"bold {ORANGE}")
        t.append("─" * 36 + "\n", style=DIMMER)
        for i, name in enumerate(self._models):
            is_current = name == self.current
            is_cursor = i == self._cursor
            if is_cursor:
                t.append(f"  ▸ ", style=f"bold {AMBER}")
                t.append(f"{name}", style=f"bold {AMBER}")
            elif is_current:
                t.append(f"  ● ", style=AMBER)
                t.append(f"{name}", style=AMBER)
            else:
                t.append(f"    ", style=DIM)
                t.append(f"{name}", style=WHITE)
            desc = {"auto": "routes via local model", "claude": "Claude Code",
                    "local": "Qwen3-14B (MLX)", "openai": "GPT-4o"}.get(name, "")
            if desc:
                t.append(f"  {desc}", style=DIM)
            t.append("\n")
        self.query_one("#model-list", Static).update(t)

    def action_move_up(self):
        self._cursor = (self._cursor - 1) % len(self._models)
        self._render_list()

    def action_move_down(self):
        self._cursor = (self._cursor + 1) % len(self._models)
        self._render_list()

    def action_select_model(self):
        self.dismiss(self._models[self._cursor])

    def action_cancel(self):
        self.dismiss(None)


# ── Widgets ──────────────────────────────────────────────────────────────────

class StatsBar(Static):
    DEFAULT_CSS = f"""
    StatsBar {{
        height: 2;
        background: {BG_PANEL};
        padding: 0 0;
    }}
    """

    def render_bar(self, name="", done=0, total=0, model="auto",
                   resolved_model="", elapsed="0s", active="", status="idle",
                   dory=False):
        t = Text(no_wrap=True, overflow="ellipsis")

        # ── Row 1: content ────────────────────────────────────────────
        t.append(" ◆ Grid", style=f"bold {ORANGE}")
        t.append("  ", style=DIM)

        # Tasks / mission name
        if total > 0:
            color = GREEN if done == total else AMBER if done > 0 else WHITE
            t.append(f"{done}/{total} tasks", style=color)
            if active:
                t.append(f"  ● {active[:28]}", style=AMBER)
            elif name:
                t.append(f"  {name[:28]}", style=DIM)
        elif name:
            t.append(f"{name[:35]}", style=WHITE)
        else:
            t.append("idle", style=DIM)

        if dory:
            t.append(f"  ◈ dory", style=f"bold {AMBER}")

        # Right-aligned section (model + sys stats + elapsed)
        right = Text(no_wrap=True, overflow="ellipsis")
        if model == "auto" and resolved_model:
            right.append(f"auto→{resolved_model}", style=TEAL)
        else:
            right.append(f"{model}", style=TEAL)

        right.append("  ", style=DIM)
        right.append(f"{elapsed} ", style=AMBER)

        # Combine: left content + padding + right content
        t.append("  ")
        t.append_text(right)

        # ── Row 2: separator ──────────────────────────────────────────
        t.append("\n")
        # Left accent (orange for active, dim for idle)
        accent_width = 24
        fill_width = 80
        if total > 0 and done < total:
            t.append("━" * accent_width, style=ORANGE)
        else:
            t.append("━" * accent_width, style=DIMMER)
        t.append("─" * fill_width, style=DIMMER)

        self.update(t)


class ModeBar(Static):
    """Command mode selector: Ask / Plan / Research."""
    DEFAULT_CSS = f"""
    ModeBar {{
        height: 1;
        padding: 0 1;
        background: {BG_PANEL};
        dock: bottom;
    }}
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self._mode = "ask"

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, val):
        self._mode = val
        self._render()

    def _refresh_display(self):
        t = Text()
        modes = [("ask", "Ask"), ("plan", "Plan"), ("research", "Research")]
        t.append(" Mode: ", style=DIM)
        for i, (key, label) in enumerate(modes):
            if i > 0:
                t.append("  ", style=DIM)
            if key == self._mode:
                t.append(f" {label} ", style=f"bold on {ORANGE} #0a0a0a")
            else:
                t.append(f" {label} ", style=f"{PENDING_GRAY}")
        t.append("    Tab to switch", style=DIM)
        self.update(t)

    def on_mount(self):
        self._refresh_display()

    def render(self):
        # Fallback for before on_mount
        t = Text()
        modes = [("ask", "Ask"), ("plan", "Plan"), ("research", "Research")]
        t.append(" Mode: ", style=DIM)
        for i, (key, label) in enumerate(modes):
            if i > 0:
                t.append("  ", style=DIM)
            if key == self._mode:
                t.append(f" {label} ", style=f"bold on {ORANGE} #0a0a0a")
            else:
                t.append(f" {label} ", style=f"{PENDING_GRAY}")
        t.append("    Tab to switch", style=DIM)
        return t

    def next_mode(self):
        modes = ["ask", "plan", "research"]
        idx = modes.index(self._mode)
        self._mode = modes[(idx + 1) % len(modes)]
        self._refresh_display()
        return self._mode

    def on_click(self, event):
        # Cycle on click
        self.next_mode()


class TaskList(Static):
    DEFAULT_CSS = f"""
    TaskList {{
        border: solid {BORDER};
        height: 100%;
        padding: 0 1;
        background: {BG_PANEL};
        overflow-y: auto;
    }}
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self._tasks = []
        self._slug = ""
        self._spinner_idx = 0

    def set_tasks(self, tasks, slug):
        self._tasks = tasks
        self._slug = slug
        self.refresh_display()

    def tick_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER_FRAMES)

    def refresh_display(self, state=None):
        if state is None:
            state = read_state()
        ms = state.get(self._slug, {})

        t = Text()
        t.append(" Tasks", style=f"bold {ORANGE}")
        if self._tasks:
            done = sum(1 for task in self._tasks if ms.get(task["id"]) == "completed")
            t.append(f"  {done}/{len(self._tasks)}", style=DIM)
        t.append("\n")
        t.append("─" * 34 + "\n", style=f"{ORANGE}")

        if not self._tasks:
            t.append("\n  waiting for plan…\n", style=DIM)
        else:
            for i, task in enumerate(self._tasks):
                tid = task.get("id", "?")
                name = task.get("name", tid)
                ttype = task.get("type", "code")
                status = ms.get(tid, "pending")

                if status == "running":
                    icon = SPINNER_FRAMES[self._spinner_idx]
                    color = AMBER
                else:
                    icon, color = STATUS_ICON.get(status, ("·", PENDING_GRAY))

                t.append(f"\n ◆ ", style=f"{color}")
                t.append(f"{icon} ", style=f"bold {color}")

                label = name[:26]
                if status == "running":
                    t.append(f"{label}", style=f"bold {AMBER}")
                elif status == "completed":
                    t.append(f"{label}", style=GREEN)
                elif status == "failed":
                    t.append(f"{label}", style=RED)
                else:
                    t.append(f"{label}", style=DIM)

                type_color = {
                    "research": CYAN, "synthesis": AMBER,
                    "gap-analysis": AMBER, "code": DIM
                }.get(ttype, DIM)
                t.append(f" [{ttype[:3]}]", style=type_color)

        self.update(t)


class DetailView(Static):
    DEFAULT_CSS = f"""
    DetailView {{
        border: solid {BORDER};
        height: 100%;
        padding: 0 1;
        background: {BG_PANEL};
        overflow-y: auto;
    }}
    """

    def show_task(self, task, status="pending"):
        icon, color = STATUS_ICON.get(status, ("·", PENDING_GRAY))
        t = Text()

        t.append(" Active Task  ", style=f"bold {ORANGE}")
        t.append(f"{task.get('id', '')}", style=f"bold {color}")
        t.append("\n")
        t.append("━" * 50 + "\n", style=f"{ORANGE}")

        t.append(f"\n {icon} ", style=f"bold {color}")
        t.append(f"{task.get('name', '')}\n", style=f"bold {WHITE}")

        ms = task.get("milestone", "")
        ttype = task.get("type", "code")
        if ms:
            t.append(f"\n  milestone   ", style=DIM)
            t.append(f"{ms}\n", style=AMBER)
        t.append(f"  type        ", style=DIM)
        t.append(f"{ttype}\n", style=WHITE)

        pre = task.get("preconditions", [])
        if pre:
            t.append(f"\n  Preconditions\n", style=f"bold {DIM}")
            for p in pre:
                t.append(f"    → {p}\n", style=DIM)

        expected = task.get("expected", "")
        if expected:
            t.append(f"\n  Expected Behavior\n", style=f"bold {DIM}")
            lines = expected.split(". ")
            for line in lines[:4]:
                if line.strip():
                    t.append(f"    · {line.strip()[:70]}\n", style=WHITE)

        prompt = task.get("prompt", "")
        if prompt:
            t.append(f"\n  Prompt\n", style=f"bold {DIM}")
            snippet = prompt[:400] + ("…" if len(prompt) > 400 else "")
            for line in snippet.split("\n")[:8]:
                t.append(f"    {line}\n", style=DIM)
            if prompt.count("\n") > 8:
                t.append(f"    … ({len(prompt)} chars total)\n", style=DIMMER)

        self.update(t)

    def show_idle(self, msg=""):
        t = Text()
        t.append(" Active Task\n", style=f"bold {ORANGE}")
        t.append("━" * 50 + "\n", style=f"{ORANGE}")
        if msg:
            t.append(f"\n  {msg}\n", style=AMBER)
        else:
            t.append(f"\n  No active task\n", style=DIM)
        self.update(t)

    def show_prompt_display(self, prompt_text):
        """Show the prompt being sent to Claude."""
        t = Text()
        t.append(" Prompt Sent\n", style=f"bold {ORANGE}")
        t.append("━" * 50 + "\n\n", style=f"{ORANGE}")
        for line in prompt_text.split("\n")[:30]:
            t.append(f"  {line}\n", style=WHITE)
        if prompt_text.count("\n") > 30:
            t.append(f"\n  … ({len(prompt_text)} chars total)\n", style=DIM)
        self.update(t)


class LiveLog(RichLog):
    DEFAULT_CSS = f"""
    LiveLog {{
        border: solid {BORDER};
        background: {BG_DARK};
        height: 100%;
        scrollbar-color: {DIMMER};
        scrollbar-background: {BG_DARK};
    }}
    """

    def push(self, line, style=None):
        clean = strip_ansi(line).rstrip()
        if not clean:
            return
        self.write(Text(clean, style=style or DIM))

    def push_question(self, prompt: str, model: str = ""):
        """Display a submitted question cleanly."""
        self.write(Text(""))
        header = Text()
        header.append("  You", style=f"bold {WHITE}")
        if model:
            header.append(f"  ·  {model}", style=DIM)
        self.write(header)
        self.write(Text(f"  {'─' * 50}", style=DIMMER))
        for line in prompt.strip().splitlines():
            self.write(Text(f"  {line}", style=WHITE))
        self.write(Text(""))

    def push_answer_header(self, model: str = ""):
        """Display the answer header before streaming begins."""
        t = Text()
        t.append("  Grid", style=f"bold {ORANGE}")
        if model:
            t.append(f"  ·  {model}", style=DIM)
        self.write(t)
        self.write(Text(f"  {'─' * 50}", style=DIMMER))

    def push_answer_line(self, line: str):
        """Display a line of the answer with indentation."""
        clean = strip_ansi(line).rstrip()
        if not clean:
            self.write(Text(""))
            return
        self.write(Text(f"  {clean}", style=WHITE))

    def push_separator(self):
        self.write(Text(f"  {'╌' * 50}", style=DIMMER))
        self.write(Text(""))


class EventLog(RichLog):
    DEFAULT_CSS = f"""
    EventLog {{
        border: solid {BORDER};
        background: {BG_DARK};
        height: 100%;
        scrollbar-color: {DIMMER};
        scrollbar-background: {BG_DARK};
    }}
    """

    def event(self, source, msg, style=None):
        ts = datetime.now().strftime("%H:%M:%S")
        t = Text()
        t.append(f"{ts} ", style=DIM)
        t.append(f"{source:<20} ", style=AMBER)
        t.append(msg, style=style or WHITE)
        self.write(t)


class BottomBar(Static):
    """Custom footer bar with keybinding hints."""
    DEFAULT_CSS = f"""
    BottomBar {{
        height: 1;
        background: {BG_PANEL};
        color: {DIM};
        padding: 0 1;
        dock: bottom;
    }}
    """

    def render(self):
        t = Text()
        keys = [
            ("^S", "Send"),
            ("m", "Model"),
            ("s", "Status"),
            ("r", "Retry"),
            ("d", "Dory"),
            ("q", "Quit"),
            ("Tab", "Mode"),
        ]
        for i, (key, label) in enumerate(keys):
            if i > 0:
                t.append(" │ ", style=DIMMER)
            t.append(f"{key} ", style=f"bold {WHITE}")
            t.append(f"{label}", style=DIM)
        return t


class PromptArea(TextArea):
    """Multi-line prompt input. Ctrl+S to submit."""
    DEFAULT_CSS = f"""
    PromptArea {{
        background: {BG_INPUT};
        border: tall {BORDER};
        color: {WHITE};
        height: 8;
        padding: 0 1;
    }}
    PromptArea:focus {{
        border: tall {ORANGE};
    }}
    """

    BINDINGS = [
        Binding("ctrl+s", "submit_prompt", "Send  Ctrl+S"),
        Binding("tab", "cycle_mode", "Mode", show=False, priority=True),
    ]

    def action_submit_prompt(self):
        self.post_message(self.Submitted(self, self.text))

    def action_cycle_mode(self):
        self.post_message(self.CycleMode(self))

    class Submitted(Message):
        def __init__(self, area, value: str):
            super().__init__()
            self.area = area
            self.value = value

    class CycleMode(Message):
        def __init__(self, area):
            super().__init__()
            self.area = area


# ── Main App ─────────────────────────────────────────────────────────────────

class GridApp(App):

    CSS = f"""
    Screen {{
        background: {BG_DARK};
        layers: base overlay;
    }}
    #statsbar {{
        height: 2;
        dock: top;
    }}
    #main {{
        height: 1fr;
    }}
    #detail {{
        width: 5fr;
    }}
    #tasks {{
        width: 2fr;
        min-width: 36;
    }}
    #bottom {{
        height: 16;
    }}
    #live {{
        width: 5fr;
    }}
    #events {{
        width: 2fr;
    }}
    #mode-bar {{
        height: 1;
        dock: bottom;
    }}
    #prompt-input {{
        height: 8;
        dock: bottom;
        width: 100%;
    }}
    BottomBar {{
        height: 1;
        dock: bottom;
    }}
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("i", "interrupt", "Interrupt"),
        Binding("y", "confirm_yes", "Confirm", show=False),
        Binding("n", "confirm_no", "Cancel", show=False),
        Binding("s", "show_status", "Status"),
        Binding("m", "select_model", "Model"),
        Binding("r", "retry_failed", "Retry"),
        Binding("d", "toggle_dory", "Dory"),
        Binding("ctrl+p", "focus_input", "Prompt"),
    ]

    def __init__(self, args):
        super().__init__()
        self.raw_args = args
        self.start_time = time.time()
        self.proc = None
        self._waiting = False
        self._last_state = {}
        self._last_active = None
        self._log_pos = {}
        self._tasks = []
        self._slug = ""
        self._mission_complete = False
        self._resolved_model = ""
        self._spinner_idx = 0
        self._dory = False

        # Parse --model flag (default: auto)
        self._model = "auto"
        self._pass_args = list(args)
        i = 0
        while i < len(self._pass_args):
            if self._pass_args[i] == "--model" and i + 1 < len(self._pass_args):
                self._model = self._pass_args[i + 1]
                self._pass_args.pop(i)
                self._pass_args.pop(i)
            else:
                i += 1

        # Determine display name
        cmd = self._pass_args[0] if self._pass_args else ""
        if cmd not in ("plan", "research", "ask", "review", "status", "models"):
            data = read_mission_json(cmd)
            if data:
                self._tasks = data.get("tasks", [])
                self._slug = slugify(data.get("name", cmd))
                self._name = data.get("name", cmd)
            else:
                self._name = cmd
        elif cmd == "plan":
            self._name = "Generating plan…"
        elif cmd == "research":
            self._name = "Research mission…"
        elif cmd == "ask":
            self._name = "Quick ask"
        else:
            self._name = " ".join(self._pass_args) if self._pass_args else ""

        self._idle = len(self._pass_args) == 0

    def compose(self) -> ComposeResult:
        yield StatsBar(id="statsbar")
        with Horizontal(id="main"):
            yield DetailView(id="detail")
            yield TaskList(id="tasks")
        with Horizontal(id="bottom"):
            yield LiveLog(id="live", highlight=False, markup=False)
            yield EventLog(id="events", highlight=False, markup=False)
        yield ModeBar(id="mode-bar")
        yield PromptArea(
            "",
            id="prompt-input",
            language=None,
            theme="css",
            show_line_numbers=False,
        )
        yield BottomBar(id="bottom-bar")

    def on_mount(self):
        tp = self.query_one("#tasks", TaskList)
        tp.set_tasks(self._tasks, self._slug)

        detail = self.query_one("#detail", DetailView)
        if self._idle:
            detail.show_idle(
                "◆ Grid — Type a prompt below.\n"
                "  Tab to switch Ask / Plan / Research.\n\n"
                "  Memory & Knowledge:\n"
                "  /remember <fact>      teach Grid about you\n"
                "  /forget [pattern]     view or remove memories\n"
                "  /learn <mission>      extract knowledge from research\n"
                "  /knowledge [query]    browse or search knowledge base\n"
                "  /clear                reset conversation\n\n"
                "  d dory · m model · s status · r retry · q quit"
            )
            self.query_one("#prompt-input", PromptArea).focus()
        elif self._pass_args and self._pass_args[0] == "ask":
            prompt = " ".join(self._pass_args[1:])
            detail.show_prompt_display(prompt)
        elif self._tasks:
            detail.show_idle("Mission loaded. Starting…")
        else:
            prompt = " ".join(self._pass_args[1:]) if len(self._pass_args) > 1 else ""
            if prompt:
                detail.show_prompt_display(prompt)
            else:
                detail.show_idle("Starting…")

        self._refresh_stats()
        self.set_interval(0.4, self._poll)
        if self._idle:
            ev = self.query_one("#events", EventLog)
            missions = list_missions()
            if missions:
                ev.event("history", "Recent missions:", DIM)
                for name, d, f, total in missions[-5:]:
                    status_str = f"{d}/{total} done"
                    if f > 0:
                        status_str += f", {f} failed"
                    color = GREEN if d == total else RED if f > 0 else DIM
                    ev.event("  " + name[:18], status_str, color)
        else:
            self.run_mission()

    def _refresh_stats(self):
        state = read_state()
        ms = state.get(self._slug, {})
        total = len(self._tasks)
        done = sum(1 for v in ms.values() if v == "completed")
        active = next(
            (t["id"] for t in self._tasks if ms.get(t["id"]) == "running"), ""
        )
        self.query_one("#statsbar", StatsBar).render_bar(
            name=self._name,
            done=done,
            total=total,
            model=self._model,
            resolved_model=self._resolved_model,
            elapsed=elapsed_str(self.start_time),
            active=active,
            dory=self._dory,
        )

    def _poll(self):
        state = read_state()
        ms = state.get(self._slug, {})

        # Tick spinner
        self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER_FRAMES)
        task_list = self.query_one("#tasks", TaskList)
        task_list.tick_spinner()

        for tid, status in ms.items():
            if self._last_state.get(tid) != status:
                self._last_state[tid] = status
                ev = self.query_one("#events", EventLog)
                if status == "completed":
                    ev.event(tid, "completed ✓", GREEN)
                elif status == "failed":
                    ev.event(tid, "FAILED ✗", RED)
                elif status == "running":
                    ev.event(tid, "started ▸", AMBER)
                    task = next((t for t in self._tasks if t["id"] == tid), None)
                    if task:
                        self.query_one("#detail", DetailView).show_task(task, "running")
                    self._last_active = tid

        # Tail active task log
        active = next((tid for tid, s in ms.items() if s == "running"), None)
        if active:
            log_file = LOGS_DIR / f"{active}.log"
            if log_file.exists():
                pos = self._log_pos.get(active, 0)
                try:
                    with open(log_file) as f:
                        f.seek(pos)
                        chunk = f.read()
                        self._log_pos[active] = f.tell()
                    if chunk:
                        ll = self.query_one("#live", LiveLog)
                        for line in chunk.splitlines():
                            ll.push(line)
                except Exception:
                    pass

        # Update detail for completed/failed
        if self._last_active:
            s = ms.get(self._last_active, "pending")
            if s in ("completed", "failed"):
                task = next(
                    (t for t in self._tasks if t["id"] == self._last_active), None
                )
                if task:
                    self.query_one("#detail", DetailView).show_task(task, s)

        task_list.refresh_display(state)
        self._refresh_stats()

    @work(thread=True)
    def run_mission(self):
        if not self._pass_args:
            return

        cmd = ["bash", str(MISSION_SH)]
        if self._model != "auto":
            cmd += ["--model", self._model]
        cmd += self._pass_args

        ev = self.query_one("#events", EventLog)
        ll = self.query_one("#live", LiveLog)

        self.call_from_thread(
            ev.event, "grid", f"→ {' '.join(self._pass_args)}", ORANGE
        )
        self.call_from_thread(
            ev.event, "grid", f"model: {self._model}", CYAN
        )

        is_ask = len(self._pass_args) > 0 and self._pass_args[0] == "ask"
        user_prompt = " ".join(self._pass_args[1:]) if is_ask and len(self._pass_args) > 1 else ""

        try:
            env = os.environ.copy()
            if self._dory:
                env["DORY_MODE"] = "1"
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                cwd=str(GRID_DIR),
                env=env,
            )

            # For ask mode: show the question first, then stream the answer cleanly
            if is_ask and user_prompt:
                self.call_from_thread(ll.push_question, user_prompt, self._model)

            buf = ""
            in_answer = False  # True once we're past the routing preamble in ask mode

            while True:
                ch = self.proc.stdout.read(1)
                if not ch:
                    break
                buf += ch

                if ch == "\n":
                    clean = strip_ansi(buf).rstrip()

                    if is_ask:
                        # Skip empty lines before answer starts
                        lower = clean.lower()
                        is_preamble = (
                            "asking" in lower or
                            "routed to:" in lower or
                            "saved to knowledge" in lower or
                            "dory mode" in lower or
                            "injecting relevant" in lower or
                            not clean
                        )
                        if is_preamble:
                            # Still parse routing info for model detection
                            if clean and self._model == "auto":
                                self._parse_resolved_model(clean)
                        else:
                            # First real content line — show answer header
                            if not in_answer:
                                in_answer = True
                                model_label = self._resolved_model or self._model
                                self.call_from_thread(ll.push_answer_header, model_label)
                            self.call_from_thread(ll.push_answer_line, clean)
                    else:
                        # Non-ask mode: stream as before
                        if clean:
                            self.call_from_thread(ll.push, clean)
                            if self._model == "auto":
                                self._parse_resolved_model(clean)

                    if "Plan saved to" in clean or "plan saved" in clean.lower():
                        self._try_load_plan(clean)
                    buf = ""

                clean_buf = strip_ansi(buf)
                if "[y/N]" in clean_buf or "[Y/n]" in clean_buf:
                    self.call_from_thread(
                        ll.push, clean_buf.strip(), f"bold {AMBER}"
                    )
                    self.call_from_thread(
                        ev.event, "grid",
                        "Waiting — press Y to run, N to cancel", AMBER
                    )
                    self.call_from_thread(self._set_waiting, True)
                    buf = ""

            self.proc.wait()
            rc = self.proc.returncode
            self.call_from_thread(self._set_waiting, False)
            self._mission_complete = True

            if is_ask and in_answer:
                self.call_from_thread(ll.push_separator)

            if rc == 0:
                self.call_from_thread(ev.event, "grid", "done ✓", GREEN)
                if not is_ask:
                    self.call_from_thread(
                        self.query_one("#detail", DetailView).show_idle,
                        "Mission complete ✓  —  Type below to continue"
                    )
            else:
                self.call_from_thread(ev.event, "grid", f"Exited with code {rc}", RED)

        except Exception as e:
            self.call_from_thread(ev.event, "error", str(e), RED)

    def _parse_resolved_model(self, line):
        """Extract resolved model from mission.sh output when using auto mode."""
        lower = line.lower()
        # Match patterns like "Running with model: local" or "Running with model: claude"
        m = re.search(r'running with model:\s*(\S+)', lower)
        if m:
            resolved = m.group(1).strip()
            self._resolved_model = resolved
            self.call_from_thread(
                self.query_one("#events", EventLog).event,
                "grid", f"auto → {resolved}", CYAN
            )
            return
        # Match "Asking auto..." -> look for "routed to local" / "routed to claude"
        m2 = re.search(r'routed?\s+to\s+(\S+)', lower)
        if m2:
            resolved = m2.group(1).strip()
            self._resolved_model = resolved
            self.call_from_thread(
                self.query_one("#events", EventLog).event,
                "grid", f"auto → {resolved}", CYAN
            )
            return
        # Match "Routed to: local (reason)" from ask mode
        m_ask = re.search(r'routed to:\s*(\S+)', lower)
        if m_ask:
            resolved = m_ask.group(1).strip()
            self._resolved_model = resolved
            # Extract reason if present
            reason_match = re.search(r'routed to:\s*\S+.*?\((.+?)\)', line, re.IGNORECASE)
            reason = reason_match.group(1) if reason_match else ""
            self.call_from_thread(
                self.query_one("#events", EventLog).event,
                "grid", f"auto → {resolved}" + (f" ({reason[:60]})" if reason else ""), CYAN
            )
            return
        # Match "using local" or "using claude"
        m3 = re.search(r'using\s+(local|claude)\b', lower)
        if m3:
            resolved = m3.group(1).strip()
            self._resolved_model = resolved
            return
        # Match "→ local" or "→ claude" from auto router
        m4 = re.search(r'→\s*(local|claude)\b', line)
        if m4:
            resolved = m4.group(1).strip()
            self._resolved_model = resolved
            self.call_from_thread(
                self.query_one("#events", EventLog).event,
                "grid", f"auto → {resolved}", CYAN
            )
            return

    def _try_load_plan(self, line):
        m = re.search(r'execplans/([^\s]+\.json)', line)
        if not m:
            return
        path = KNOWLEDGE_DIR / "execplans" / Path(m.group(1)).name
        if not path.exists():
            path = Path(m.group(1))
        try:
            data = json.loads(path.read_text())
            self._tasks = data.get("tasks", [])
            self._slug = slugify(data.get("name", ""))
            self._name = data.get("name", self._name)
            self.call_from_thread(
                self.query_one("#tasks", TaskList).set_tasks,
                self._tasks, self._slug,
            )
            self.call_from_thread(
                self.query_one("#events", EventLog).event,
                "grid", f"Plan loaded: {len(self._tasks)} tasks", AMBER,
            )
        except Exception:
            pass

    def _set_waiting(self, val):
        self._waiting = val
        if val:
            self.query_one("#detail", DetailView).show_idle(
                "Plan ready — press Y to execute, N to cancel"
            )

    # ── Input handling ───────────────────────────────────────────────────────

    def on_prompt_area_submitted(self, event: PromptArea.Submitted):
        """Handle follow-up prompts from the text area (Ctrl+S)."""
        prompt = event.value.strip()
        if not prompt:
            return
        event.area.clear()

        ev = self.query_one("#events", EventLog)
        detail = self.query_one("#detail", DetailView)

        # Check for slash commands first
        if prompt.startswith("/plan "):
            cmd_args = ["plan", prompt[6:]]
        elif prompt.startswith("/research "):
            cmd_args = ["research", prompt[10:]]
        elif prompt.startswith("/status"):
            self.action_show_status()
            return
        elif prompt.startswith("/retry"):
            self.action_retry_failed()
            return
        elif prompt.startswith("/clear") or prompt.startswith("/new"):
            cmd_args = ["clear"]
            ev.event("grid", "Conversation cleared", GREEN)
            # Run it but don't display as a mission
            subprocess.run(
                ["bash", str(MISSION_SH), "clear"],
                cwd=str(GRID_DIR), capture_output=True,
            )
            return
        elif prompt.startswith("/remember "):
            fact = prompt[10:].strip()
            subprocess.run(
                ["bash", str(MISSION_SH), "remember", fact],
                cwd=str(GRID_DIR), capture_output=True,
            )
            ev.event("grid", f"Remembered: {fact}", GREEN)
            return
        elif prompt.startswith("/forget"):
            pattern = prompt[7:].strip()
            if pattern:
                subprocess.run(
                    ["bash", str(MISSION_SH), "forget", pattern],
                    cwd=str(GRID_DIR), capture_output=True,
                )
                ev.event("grid", f"Forgot: {pattern}", AMBER)
            else:
                # Show memories
                if MEMORY_FILE.exists():
                    content = MEMORY_FILE.read_text().strip()
                    if content:
                        detail.show_prompt_display(f"Grid Memories:\n\n{content}")
                    else:
                        ev.event("grid", "No memories yet", DIM)
                else:
                    ev.event("grid", "No memories yet", DIM)
            return
        elif prompt.startswith("/learn"):
            mission_slug = prompt[6:].strip()
            if mission_slug:
                ev.event("grid", f"Learning from: {mission_slug}", AMBER)
                cmd_args = ["learn", mission_slug]
            else:
                # List available missions
                missions_dir = KNOWLEDGE_DIR / "missions"
                if missions_dir.exists():
                    slugs = [d.name for d in missions_dir.iterdir() if d.is_dir()]
                    if slugs:
                        detail.show_prompt_display(
                            "Available missions to learn from:\n\n"
                            + "\n".join(f"  /learn {s}" for s in slugs)
                        )
                    else:
                        ev.event("grid", "No completed missions to learn from", DIM)
                return
        elif prompt.startswith("/knowledge"):
            query = prompt[10:].strip()
            concepts_dir = KNOWLEDGE_DIR / "concepts"
            if not concepts_dir.exists() or not list(concepts_dir.glob("*.md")):
                detail.show_prompt_display(
                    "Knowledge base is empty.\n\n"
                    "Use /learn <mission-slug> to extract concepts from completed research."
                )
            else:
                files = list(concepts_dir.glob("*.md"))
                if query:
                    # Show search hint — actual search happens in shell
                    cmd_args = ["knowledge", query]
                else:
                    lines = ["Knowledge Base:\n"]
                    for f in sorted(files):
                        lines.append(f"  ◆ {f.stem}")
                    lines.append("\nUse /knowledge <query> to search, or /learn <mission> to add.")
                    detail.show_prompt_display("\n".join(lines))
                    return
        elif prompt.startswith("/model "):
            new_model = prompt[7:].strip()
            available = selectable_models()
            if new_model in available:
                self._model = new_model
                self._resolved_model = ""
                ev.event("grid", f"Model → {new_model}", CYAN)
                self._refresh_stats()
            else:
                ev.event("grid", f"Unknown model: {new_model}. Available: {', '.join(available)}", RED)
            return
        else:
            # Use mode bar to determine command
            mode = self.query_one("#mode-bar", ModeBar).mode
            if mode == "plan":
                cmd_args = ["plan", prompt]
            elif mode == "research":
                cmd_args = ["research", prompt]
            else:
                cmd_args = ["ask", prompt]

        self._pass_args = cmd_args
        self._idle = False
        self._name = cmd_args[0] + ": " + cmd_args[1][:40] if len(cmd_args) > 1 else cmd_args[0]
        self.start_time = time.time()
        self._mission_complete = False
        self._resolved_model = ""

        detail.show_prompt_display(prompt)
        ev.event("input", f"[{cmd_args[0]}] → {prompt[:60]}", ORANGE)

        self.run_mission()

    # ── Key bindings ─────────────────────────────────────────────────────────

    def on_prompt_area_cycle_mode(self, message: PromptArea.CycleMode):
        """Handle Tab pressed inside PromptArea — cycle mode."""
        self.action_cycle_mode()

    def action_cycle_mode(self):
        """Cycle through command modes."""
        mode_bar = self.query_one("#mode-bar", ModeBar)
        new_mode = mode_bar.next_mode()
        self.query_one("#events", EventLog).event("mode", f"→ {new_mode}", DIM)

    def action_confirm_yes(self):
        if self._waiting and self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.write("y\n")
                self.proc.stdin.flush()
            except Exception:
                pass
            self._waiting = False
            self.query_one("#events", EventLog).event(
                "grid", "Confirmed → executing", GREEN
            )

    def action_confirm_no(self):
        if self._waiting and self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.write("n\n")
                self.proc.stdin.flush()
            except Exception:
                pass
            self._waiting = False
            self.query_one("#events", EventLog).event(
                "grid", "Cancelled", RED
            )

    def action_interrupt(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.query_one("#events", EventLog).event(
                "grid", "Interrupted ⚡", RED
            )

    def action_show_status(self):
        state = read_state()
        ms = state.get(self._slug, {})
        ev = self.query_one("#events", EventLog)
        done = sum(1 for v in ms.values() if v == "completed")
        fail = sum(1 for v in ms.values() if v == "failed")
        pend = len(self._tasks) - done - fail
        ev.event("status", f"{done} done · {fail} failed · {pend} pending", AMBER)

        missions = list_missions()
        if len(missions) > 1:
            for name, d, f, total in missions[-5:]:
                ev.event("mission", f"{name}: {d}/{total} done, {f} failed", DIM)

    def action_select_model(self):
        def on_dismiss(model):
            if model:
                self._model = model
                self._resolved_model = ""
                self.query_one("#events", EventLog).event(
                    "grid", f"Model → {model}", CYAN
                )
                self._refresh_stats()

        self.push_screen(ModelSelector(self._model), on_dismiss)

    def action_retry_failed(self):
        """Mark all failed tasks with #redo in their notes."""
        if not self._slug:
            return
        state = read_state()
        ms = state.get(self._slug, {})
        ev = self.query_one("#events", EventLog)
        count = 0

        for tid, status in ms.items():
            if status == "failed":
                note_path = KNOWLEDGE_DIR / "missions" / self._slug / f"{tid}.md"
                if note_path.exists():
                    content = note_path.read_text()
                    if "#redo" not in content:
                        content = content.rstrip() + "\n#redo\n"
                        note_path.write_text(content)
                        count += 1

        if count > 0:
            ev.event("grid", f"Marked {count} failed tasks for retry", AMBER)
            ev.event("grid", "Re-run the mission to execute them", DIM)
        else:
            ev.event("grid", "No failed tasks to retry", DIM)

    def action_toggle_dory(self):
        """Toggle Dory mode (ephemeral — nothing saved to disk)."""
        self._dory = not self._dory
        ev = self.query_one("#events", EventLog)
        if self._dory:
            ev.event("grid", "Dory mode ON — nothing will be saved", AMBER)
        else:
            ev.event("grid", "Dory mode OFF — saving normally", GREEN)
        self._refresh_stats()

    def action_focus_input(self):
        """Focus the prompt input."""
        self.query_one("#prompt-input", PromptArea).focus()

    def action_quit(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.exit()


# ── Entry ────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    GridApp(args).run()


if __name__ == "__main__":
    main()
