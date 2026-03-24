"""Verification agent — independently fact-checks individual claims.

CRITICAL: The verifier operates with a CLEAN context. It does NOT see the
original agent's chain-of-thought or reasoning. It only receives:
- The specific claim to verify
- The rubric instructions (what to check for)

This prevents confirmation bias — the verifier gathers evidence independently.
"""

from __future__ import annotations

from verification.llm import call_llm_json
from verification.models import VerificationResult, VerificationTask
from verification.taxonomy import build_verification_prompt


def verify(task: VerificationTask, model: str | None = None) -> VerificationResult:
    """Verify a single claim independently.

    The verifier only sees the claim and rubric — NOT the original agent's
    reasoning. This ensures unbiased verification.

    Args:
        task: The verification task containing the claim and rubric.
        model: Which model to use for verification (None = default).

    Returns:
        VerificationResult with status, evidence, confidence, and explanation.
    """
    prompt = build_verification_prompt(task.claim, task.rubric)

    try:
        response = call_llm_json(prompt, model=model)
    except (RuntimeError, ValueError) as e:
        # If the LLM call fails, return an uncertain result
        return VerificationResult(
            task=task,
            status="uncertain",
            evidence="",
            confidence=0.0,
            explanation=f"Verification failed: {e}",
        )

    status = response.get("status", "uncertain")
    if status not in ("confirmed", "refuted", "uncertain"):
        status = "uncertain"

    confidence = response.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5
    confidence = max(0.0, min(1.0, float(confidence)))

    return VerificationResult(
        task=task,
        status=status,
        evidence=response.get("evidence", ""),
        confidence=confidence,
        explanation=response.get("explanation", ""),
    )
