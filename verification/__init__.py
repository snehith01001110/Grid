"""DeepVerifier — inference-time verification pipeline for Grid.

Adds a structured verification layer that independently fact-checks and validates
agent outputs using a failure taxonomy converted into executable rubrics.

Based on: "Inference-Time Scaling of Verification: Self-Evolving Deep Research
Agents via Test-Time Rubric-Guided Verification" (arXiv:2601.15808)
"""

from verification.models import (
    VerificationTask,
    VerificationResult,
    VerificationVerdict,
)
from verification.pipeline import verify_output

__all__ = [
    "VerificationTask",
    "VerificationResult",
    "VerificationVerdict",
    "verify_output",
]
