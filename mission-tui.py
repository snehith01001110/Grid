#!/Users/nayak/Documents/Grid/.venv/bin/python3
"""Grid Mission Control — Terminal UI v2"""

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
from textual.widgets import Header, Footer, Static, RichLog, Input, Label, TextArea
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive
from textual import work
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.message import Message
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
# Warm dark theme — blacks, deep browns, with hot orange/red/yellow accents
BG_DARK = "#0a0604"
BG_PANEL = "#110a06"
BG_INPUT = "#1a0e08"
BORDER = "#2a1508"
BORDER_FOCUS = "#ff6a00"

ORANGE = "#ff6a00"
AMBER = "#ff9500"
YELLOW = "#ffd000"
RED = "#ff3333"
GREEN = "#33ff66"
CYAN = "#00ddff"
WHITE = "#f0e6d8"
DIM = "#665544"
DIMMER = "#443322"

STATUS_ICON = {
    "completed": ("✓", GREEN),
    "failed": ("✗", RED),
    "running": ("▸", YELLOW),
    "skipped": ("⊘", DIM),
    "pending": ("·", DIMMER),
    "blocked": ("⏸", DIM),
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
                t.append(f"  ▸ ", style=f"bold {YELLOW}")
                t.append(f"{name}", style=f"bold {YELLOW}")
            elif is_current:
                t.append(f"  ● ", style=AMBER)
                t.append(f"{name}", style=AMBER)
            else:
                t.append(f"    ", style=DIM)
                t.append(f"{name}", style=WHITE)
            # Description
            desc = {"auto": "routes via local model", "claude": "Claude Code",
                    "local": "Qwen3-14B (MLX)"}.get(name, "")
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
        height: 1;
        background: {BORDER};
        color: {DIM};
        padding: 0 1;
    }}
    """

    def render_bar(self, name="", done=0, total=0, model="claude",
                   elapsed="0s", active="", status="idle"):
        t = Text(overflow="fold")
        t.append(" ◆ ", style=f"bold {ORANGE}")
        t.append("Grid Mission Control  ", style=f"bold {ORANGE}")

        if name:
            display_name = name[:40] + "…" if len(name) > 40 else name
            t.append(f"{display_name}  ", style=f"bold {WHITE}")

        t.append(f"TIME ", style=DIM)
        t.append(f"{elapsed}  ", style=AMBER)

        if total > 0:
            color = GREEN if done == total else YELLOW if done > 0 else DIM
            t.append(f"Tasks ", style=DIM)
            t.append(f"{done}/{total}  ", style=color)

        t.append(f"Model ", style=DIM)
        t.append(f"{model}  ", style=CYAN)

        if active:
            t.append(f"● ", style=f"bold {YELLOW}")
            t.append(f"{active}", style=YELLOW)

        self.update(t)


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

    def set_tasks(self, tasks, slug):
        self._tasks = tasks
        self._slug = slug
        self.refresh_display()

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
        t.append("─" * 34 + "\n", style=DIMMER)

        if not self._tasks:
            t.append("\n  waiting for plan…\n", style=DIM)
        else:
            for i, task in enumerate(self._tasks):
                tid = task.get("id", "?")
                name = task.get("name", tid)
                ttype = task.get("type", "code")
                status = ms.get(tid, "pending")
                icon, color = STATUS_ICON.get(status, ("·", DIMMER))

                t.append(f"\n {icon} ", style=f"bold {color}")

                label = name[:28]
                if status == "running":
                    t.append(f"{label}", style=f"bold {YELLOW}")
                elif status == "completed":
                    t.append(f"{label}", style=GREEN)
                elif status == "failed":
                    t.append(f"{label}", style=RED)
                else:
                    t.append(f"{label}", style=DIM)

                # Type badge
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
        icon, color = STATUS_ICON.get(status, ("·", DIMMER))
        t = Text()

        # Header
        t.append(" Active Task  ", style=f"bold {ORANGE}")
        t.append(f"{task.get('id', '')}", style=f"bold {color}")
        t.append("\n")
        t.append("═" * 50 + "\n", style=DIMMER)

        # Title
        t.append(f"\n {icon} ", style=f"bold {color}")
        t.append(f"{task.get('name', '')}\n", style=f"bold {WHITE}")

        # Metadata table
        ms = task.get("milestone", "")
        ttype = task.get("type", "code")
        if ms:
            t.append(f"\n  milestone   ", style=DIM)
            t.append(f"{ms}\n", style=AMBER)
        t.append(f"  type        ", style=DIM)
        t.append(f"{ttype}\n", style=WHITE)

        # Preconditions
        pre = task.get("preconditions", [])
        if pre:
            t.append(f"\n  Preconditions\n", style=f"bold {DIM}")
            for p in pre:
                t.append(f"    → {p}\n", style=DIM)

        # Expected
        expected = task.get("expected", "")
        if expected:
            t.append(f"\n  Expected Behavior\n", style=f"bold {DIM}")
            lines = expected.split(". ")
            for line in lines[:4]:
                if line.strip():
                    t.append(f"    · {line.strip()[:70]}\n", style=WHITE)

        # Prompt preview
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
        t.append("═" * 50 + "\n", style=DIMMER)
        if msg:
            t.append(f"\n  {msg}\n", style=AMBER)
        else:
            t.append(f"\n  No active task\n", style=DIM)
        self.update(t)

    def show_prompt_display(self, prompt_text):
        """Show the prompt being sent to Claude."""
        t = Text()
        t.append(" Prompt Sent\n", style=f"bold {ORANGE}")
        t.append("═" * 50 + "\n\n", style=DIMMER)
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
        scrollbar-color: {ORANGE};
        scrollbar-background: {BG_DARK};
    }}
    """

    def push(self, line, style=None):
        clean = strip_ansi(line).rstrip()
        if not clean:
            return
        self.write(Text(clean, style=style or DIM))


class EventLog(RichLog):
    DEFAULT_CSS = f"""
    EventLog {{
        border: solid {BORDER};
        background: {BG_DARK};
        height: 100%;
        scrollbar-color: {ORANGE};
        scrollbar-background: {BG_DARK};
    }}
    """

    def event(self, source, msg, style=None):
        ts = datetime.now().strftime("%H:%M:%S")
        t = Text()
        t.append(f"{ts} ", style=DIMMER)
        t.append(f"{source:<20} ", style=AMBER)
        t.append(msg, style=style or WHITE)
        self.write(t)


class PromptArea(TextArea):
    """Multi-line prompt input. Ctrl+S to submit."""
    DEFAULT_CSS = f"""
    PromptArea {{
        background: {BG_INPUT};
        border: tall {BORDER};
        color: {WHITE};
        height: 6;
        padding: 0 1;
    }}
    PromptArea:focus {{
        border: tall {ORANGE};
    }}
    """

    BINDINGS = [
        Binding("ctrl+s", "submit_prompt", "Send  Ctrl+S"),
    ]

    def action_submit_prompt(self):
        self.post_message(self.Submitted(self, self.text))

    class Submitted(Message):
        def __init__(self, area, value: str):
            super().__init__()
            self.area = area
            self.value = value


# ── Main App ─────────────────────────────────────────────────────────────────

class GridApp(App):

    CSS = f"""
    Screen {{
        background: {BG_DARK};
        layers: base overlay;
    }}
    #statsbar {{
        height: 1;
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
    #prompt-input {{
        height: 6;
        dock: bottom;
        width: 100%;
    }}
    Footer {{
        background: {BORDER};
        color: {DIM};
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

        # Track if we launched in idle mode (no args)
        self._idle = len(self._pass_args) == 0

    def compose(self) -> ComposeResult:
        yield StatsBar(id="statsbar")
        with Horizontal(id="main"):
            yield DetailView(id="detail")
            yield TaskList(id="tasks")
        with Horizontal(id="bottom"):
            yield LiveLog(id="live", highlight=False, markup=False)
            yield EventLog(id="events", highlight=False, markup=False)
        yield PromptArea(
            "",
            id="prompt-input",
            language=None,
            theme="css",
            show_line_numbers=False,
        )
        yield Footer()

    def on_mount(self):
        tp = self.query_one("#tasks", TaskList)
        tp.set_tasks(self._tasks, self._slug)

        detail = self.query_one("#detail", DetailView)
        if self._idle:
            # Idle mode — show welcome, focus input
            detail.show_idle(
                "◆ Grid Mission Control\n\n"
                "  Type a prompt below to get started.\n\n"
                "  Commands:\n"
                "    just type        → quick ask\n"
                "    /plan <desc>     → generate & run mission\n"
                "    /research <q>    → research mission\n\n"
                "  Keys: m model · s status · r retry · q quit"
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
            # Show recent missions in event log
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
            elapsed=elapsed_str(self.start_time),
            active=active,
        )

    def _poll(self):
        state = read_state()
        ms = state.get(self._slug, {})

        for tid, status in ms.items():
            if self._last_state.get(tid) != status:
                self._last_state[tid] = status
                ev = self.query_one("#events", EventLog)
                if status == "completed":
                    ev.event(tid, "completed ✓", GREEN)
                elif status == "failed":
                    ev.event(tid, "FAILED ✗", RED)
                elif status == "running":
                    ev.event(tid, "started ▸", YELLOW)
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

        self.query_one("#tasks", TaskList).refresh_display(state)
        self._refresh_stats()

    @work(thread=True)
    def run_mission(self):
        if not self._pass_args:
            return  # idle mode — no command to run

        # Build command with model flag
        # "auto" = mission.sh default (no flag needed)
        # specific model = pass --model <name>
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

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                cwd=str(GRID_DIR),
            )

            buf = ""
            while True:
                ch = self.proc.stdout.read(1)
                if not ch:
                    break
                buf += ch

                if ch == "\n":
                    clean = strip_ansi(buf).rstrip()
                    if clean:
                        self.call_from_thread(ll.push, clean)
                    if "Plan saved to" in clean or "plan saved" in clean.lower():
                        self._try_load_plan(clean)
                    buf = ""

                clean_buf = strip_ansi(buf)
                if "[y/N]" in clean_buf or "[Y/n]" in clean_buf:
                    self.call_from_thread(
                        ll.push, clean_buf.strip(), f"bold {YELLOW}"
                    )
                    self.call_from_thread(
                        ev.event, "grid",
                        "Waiting — press Y to run, N to cancel", YELLOW
                    )
                    self.call_from_thread(self._set_waiting, True)
                    buf = ""

            self.proc.wait()
            rc = self.proc.returncode
            self.call_from_thread(self._set_waiting, False)
            self._mission_complete = True

            if rc == 0:
                self.call_from_thread(
                    ev.event, "grid", "Mission complete ✓", GREEN
                )
                self.call_from_thread(
                    self.query_one("#detail", DetailView).show_idle,
                    "Mission complete ✓  —  Type below to continue"
                )
            else:
                self.call_from_thread(
                    ev.event, "grid", f"Exited with code {rc}", RED
                )

        except Exception as e:
            self.call_from_thread(ev.event, "error", str(e), RED)

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
        """Handle follow-up prompts from the text area (Ctrl+Enter)."""
        prompt = event.value.strip()
        if not prompt:
            return
        event.area.clear()

        ev = self.query_one("#events", EventLog)
        detail = self.query_one("#detail", DetailView)

        # Determine command
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
        elif prompt.startswith("/model "):
            # Switch model inline: /model ollama
            new_model = prompt[7:].strip()
            available = selectable_models()
            if new_model in available:
                self._model = new_model
                ev.event("grid", f"Model → {new_model}", CYAN)
                self._refresh_stats()
            else:
                ev.event("grid", f"Unknown model: {new_model}. Available: {', '.join(available)}", RED)
            return
        else:
            # Default: ask
            cmd_args = ["ask", prompt]

        self._pass_args = cmd_args
        self._idle = False
        self._name = cmd_args[0] + ": " + cmd_args[1][:40] if len(cmd_args) > 1 else cmd_args[0]
        self.start_time = time.time()
        self._mission_complete = False

        detail.show_prompt_display(prompt)
        ev.event("input", f"→ {prompt[:60]}", ORANGE)

        self.run_mission()

    # ── Key bindings ─────────────────────────────────────────────────────────

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

        # Also show all missions
        missions = list_missions()
        if len(missions) > 1:
            for name, d, f, total in missions[-5:]:
                ev.event("mission", f"{name}: {d}/{total} done, {f} failed", DIM)

    def action_select_model(self):
        def on_dismiss(model):
            if model:
                self._model = model
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
    # Everything launches the TUI — even no args (idle mode)
    GridApp(args).run()


if __name__ == "__main__":
    main()
