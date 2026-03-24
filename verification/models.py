"""Data models for the verification pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VerificationTask:
    """A single claim or reasoning step to verify."""

    claim: str
    taxonomy_category: str
    subcategory: str
    rubric: str
    priority: str  # "high" | "medium" | "low"
    source_text: str = ""  # the original text this claim was extracted from

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "taxonomy_category": self.taxonomy_category,
            "subcategory": self.subcategory,
            "rubric": self.rubric,
            "priority": self.priority,
            "source_text": self.source_text,
        }


@dataclass
class VerificationResult:
    """Result of verifying a single claim."""

    task: VerificationTask
    status: str  # "confirmed" | "refuted" | "uncertain"
    evidence: str
    confidence: float  # 0.0 to 1.0
    explanation: str

    def to_dict(self) -> dict:
        return {
            "claim": self.task.claim,
            "taxonomy_category": self.task.taxonomy_category,
            "subcategory": self.task.subcategory,
            "status": self.status,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


@dataclass
class VerificationVerdict:
    """Aggregated verdict from the judge."""

    overall_status: str  # "pass" | "fail" | "needs_revision"
    confidence: float  # 0.0 to 1.0
    checks: list[VerificationResult] = field(default_factory=list)
    feedback: Optional[str] = None  # structured feedback for retry
    failed_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status,
            "confidence": self.confidence,
            "checks": [c.to_dict() for c in self.checks],
            "feedback": self.feedback,
            "failed_claims": self.failed_claims,
            "total_checks": len(self.checks),
            "passed": sum(1 for c in self.checks if c.status == "confirmed"),
            "failed": sum(1 for c in self.checks if c.status == "refuted"),
            "uncertain": sum(1 for c in self.checks if c.status == "uncertain"),
        }
