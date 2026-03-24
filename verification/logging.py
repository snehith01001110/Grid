"""Structured logging for verification traces.

Produces JSON log entries for every verification run, matching the
JSONL pattern used by .mission/routing-log.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from verification.models import VerificationVerdict

GRID_DIR = Path(__file__).resolve().parent.parent
VERIFICATION_LOG = GRID_DIR / ".mission" / "logs" / "verification.jsonl"


def log_verification_run(
    task_id: str,
    mission: str,
    agent_output: str,
    verdict: VerificationVerdict,
    wall_time: float,
    total_llm_calls: int,
    verification_model: str | None,
    verification_round: int = 1,
) -> dict:
    """Log a verification run as a structured JSON entry.

    Returns the log entry dict for testing/inspection.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task_id": task_id,
        "mission": mission,
        "original_output_hash": hashlib.sha256(
            agent_output.encode()
        ).hexdigest()[:16],
        "verification_round": verification_round,
        "decomposed_checks": len(verdict.checks),
        "passed": sum(1 for c in verdict.checks if c.status == "confirmed"),
        "failed": sum(1 for c in verdict.checks if c.status == "refuted"),
        "uncertain": sum(1 for c in verdict.checks if c.status == "uncertain"),
        "overall_verdict": verdict.overall_status,
        "confidence": round(verdict.confidence, 3),
        "failed_claims": verdict.failed_claims,
        "wall_time_seconds": round(wall_time, 1),
        "total_llm_calls": total_llm_calls,
        "verification_model": verification_model or "default",
    }

    # Append to JSONL log
    VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VERIFICATION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
