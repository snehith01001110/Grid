"""Judge agent — aggregates verification results into a final verdict.

Produces per-rubric pass/fail verdicts, an overall confidence score, and
structured feedback that can be injected back into the original agent
for retry if claims were refuted.
"""

from __future__ import annotations

from verification.llm import call_llm_json
from verification.models import VerificationResult, VerificationVerdict

JUDGE_PROMPT = """You are a verification judge. Given the results of independent fact-checking on claims extracted from an agent's output, produce a final verdict.

ORIGINAL AGENT OUTPUT (summary):
\"\"\"
{agent_output_summary}
\"\"\"

VERIFICATION RESULTS:
{verification_results}

Based on these verification results, determine:
1. Overall status: "pass" if all critical claims confirmed, "fail" if any high-priority claim refuted, "needs_revision" if uncertain or mixed results
2. Overall confidence: weighted average considering claim priority
3. If any claims failed, provide specific, actionable feedback that could be given back to the agent to fix its output

Output ONLY a JSON object (no other text):
{{
  "overall_status": "pass|fail|needs_revision",
  "confidence": 0.0 to 1.0,
  "feedback": "Specific feedback for the agent if revision needed, or null if pass",
  "reasoning": "Brief explanation of the verdict"
}}"""


def evaluate(
    results: list[VerificationResult],
    agent_output: str,
    model: str | None = None,
) -> VerificationVerdict:
    """Aggregate verification results into a final verdict.

    Args:
        results: List of VerificationResult from the verifier.
        agent_output: The original agent output (for context).
        model: Which model to use for judging (None = default).

    Returns:
        VerificationVerdict with overall status, confidence, and feedback.
    """
    if not results:
        return VerificationVerdict(
            overall_status="pass",
            confidence=1.0,
            checks=[],
            feedback=None,
            failed_claims=[],
        )

    # Collect failed claims
    failed_claims = [r.task.claim for r in results if r.status == "refuted"]

    # Quick path: if no LLM needed (all confirmed or simple cases)
    confirmed = sum(1 for r in results if r.status == "confirmed")
    refuted = sum(1 for r in results if r.status == "refuted")
    uncertain = sum(1 for r in results if r.status == "uncertain")

    # If all confirmed, skip the LLM call
    if refuted == 0 and uncertain == 0:
        avg_confidence = sum(r.confidence for r in results) / len(results)
        return VerificationVerdict(
            overall_status="pass",
            confidence=avg_confidence,
            checks=results,
            feedback=None,
            failed_claims=[],
        )

    # Build results summary for the judge prompt
    results_text = ""
    for i, r in enumerate(results, 1):
        results_text += (
            f"\n{i}. Claim: \"{r.task.claim}\"\n"
            f"   Category: {r.task.taxonomy_category}/{r.task.subcategory}\n"
            f"   Priority: {r.task.priority}\n"
            f"   Status: {r.status}\n"
            f"   Confidence: {r.confidence}\n"
            f"   Evidence: {r.evidence[:300]}\n"
            f"   Explanation: {r.explanation[:300]}\n"
        )

    prompt = JUDGE_PROMPT.format(
        agent_output_summary=agent_output[:3000],
        verification_results=results_text,
    )

    try:
        response = call_llm_json(prompt, model=model)
    except (RuntimeError, ValueError):
        # Fallback: compute verdict from raw results without LLM
        return _compute_fallback_verdict(results, failed_claims)

    status = response.get("overall_status", "needs_revision")
    if status not in ("pass", "fail", "needs_revision"):
        status = "needs_revision"

    confidence = response.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)):
        confidence = 0.5
    confidence = max(0.0, min(1.0, float(confidence)))

    feedback = response.get("feedback")
    if feedback == "null" or feedback is None:
        feedback = None

    return VerificationVerdict(
        overall_status=status,
        confidence=confidence,
        checks=results,
        feedback=feedback,
        failed_claims=failed_claims,
    )


def _compute_fallback_verdict(
    results: list[VerificationResult],
    failed_claims: list[str],
) -> VerificationVerdict:
    """Compute a verdict without an LLM call (fallback)."""
    refuted = sum(1 for r in results if r.status == "refuted")
    high_refuted = sum(
        1 for r in results if r.status == "refuted" and r.task.priority == "high"
    )
    avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0

    if high_refuted > 0:
        status = "fail"
    elif refuted > 0:
        status = "needs_revision"
    else:
        status = "pass" if avg_confidence >= 0.7 else "needs_revision"

    feedback = None
    if failed_claims:
        feedback = (
            "The following claims could not be verified and may be incorrect:\n"
            + "\n".join(f"- {c}" for c in failed_claims)
            + "\n\nPlease re-examine these claims and provide corrected information "
            "with proper source attribution."
        )

    return VerificationVerdict(
        overall_status=status,
        confidence=avg_confidence,
        checks=results,
        feedback=feedback,
        failed_claims=failed_claims,
    )
