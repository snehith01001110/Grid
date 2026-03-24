"""Configuration for the verification pipeline.

Reads verification settings from .mission/verification.conf (INI-style)
matching the pattern of .mission/models.conf.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

GRID_DIR = Path(__file__).resolve().parent.parent
VERIFICATION_CONF = GRID_DIR / ".mission" / "verification.conf"

# Defaults — used when no config file exists
DEFAULTS = {
    "enabled": "true",
    "policy": "thorough",       # quick | thorough | critical
    "max_rounds": "2",          # max verification-retry cycles
    "parallel": "true",         # run verification checks in parallel
    "model": "",                # empty = use same model as generation
    "log_results": "true",      # save verification traces
    "fail_action": "warn",      # warn | block | retry
    "max_workers": "4",         # max parallel verification threads
}


@dataclass
class VerificationConfig:
    enabled: bool = True
    policy: str = "thorough"
    max_rounds: int = 2
    parallel: bool = True
    model: str | None = None    # None = use same model as generation
    log_results: bool = True
    fail_action: str = "warn"   # warn | block | retry
    max_workers: int = 4


def load_config() -> VerificationConfig:
    """Load verification config from .mission/verification.conf."""
    values = dict(DEFAULTS)

    if VERIFICATION_CONF.exists():
        for line in VERIFICATION_CONF.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip()

    return VerificationConfig(
        enabled=values["enabled"].lower() in ("true", "1", "yes"),
        policy=values["policy"],
        max_rounds=int(values["max_rounds"]),
        parallel=values["parallel"].lower() in ("true", "1", "yes"),
        model=values["model"] or None,
        log_results=values["log_results"].lower() in ("true", "1", "yes"),
        fail_action=values["fail_action"],
        max_workers=int(values["max_workers"]),
    )


def write_default_config() -> None:
    """Write the default verification.conf if it doesn't exist."""
    if VERIFICATION_CONF.exists():
        return

    content = """# Verification Pipeline Configuration
# Based on DeepVerifier (arXiv:2601.15808)

# Enable/disable verification (true/false)
enabled=true

# Verification policy: quick (high-priority only), thorough (all), critical (all + strict)
policy=thorough

# Maximum verification-retry cycles before giving up
max_rounds=2

# Run verification checks in parallel (true/false)
parallel=true

# Model for verification LLM calls (empty = same as generation model)
# Use a cheaper model here for cost savings, e.g.: local
model=

# Save verification traces to .mission/logs/ (true/false)
log_results=true

# Action on verification failure: warn (log + continue), block (fail task), retry (re-run with feedback)
fail_action=warn

# Maximum parallel verification workers
max_workers=4
"""
    VERIFICATION_CONF.write_text(content)
