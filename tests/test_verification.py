"""Tests for the DeepVerifier verification pipeline.

Run with: python3 -m pytest tests/test_verification.py -v
"""

import json
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.taxonomy import (
    FAILURE_TAXONOMY,
    get_rubric,
    get_all_categories,
    build_verification_prompt,
)
from verification.models import (
    VerificationTask,
    VerificationResult,
    VerificationVerdict,
)
from verification.config import VerificationConfig, load_config
from verification.llm import parse_json_response


# ── Taxonomy tests ────────────────────────────────────────────────────────────


class TestTaxonomy:
    def test_taxonomy_has_five_categories(self):
        assert len(FAILURE_TAXONOMY) == 5
        expected = {
            "reasoning_errors",
            "decomposition_failures",
            "action_errors",
            "information_errors",
            "cascading_failures",
        }
        assert set(FAILURE_TAXONOMY.keys()) == expected

    def test_each_category_has_subcategories(self):
        for cat_name, cat_data in FAILURE_TAXONOMY.items():
            assert "description" in cat_data, f"{cat_name} missing description"
            assert "subcategories" in cat_data, f"{cat_name} missing subcategories"
            assert len(cat_data["subcategories"]) > 0, f"{cat_name} has no subcategories"

    def test_each_subcategory_has_rubric(self):
        for cat_name, cat_data in FAILURE_TAXONOMY.items():
            for sub_name, sub_data in cat_data["subcategories"].items():
                assert "rubric" in sub_data, f"{cat_name}/{sub_name} missing rubric"
                assert len(sub_data["rubric"]) > 20, f"{cat_name}/{sub_name} rubric too short"

    def test_get_rubric_returns_valid_prompt(self):
        rubric = get_rubric("information_errors", "factual_hallucination")
        assert "claim" in rubric.lower() or "fact" in rubric.lower()
        assert len(rubric) > 20

    def test_get_rubric_unknown_returns_empty(self):
        assert get_rubric("nonexistent", "nope") == ""

    def test_get_all_categories_flat(self):
        cats = get_all_categories()
        assert len(cats) >= 12  # at least 12 subcategories
        for cat, sub, desc, rubric in cats:
            assert cat in FAILURE_TAXONOMY
            assert len(desc) > 5
            assert len(rubric) > 20

    def test_build_verification_prompt(self):
        prompt = build_verification_prompt(
            "The market size is $50 billion",
            "Verify the numerical claim.",
        )
        assert "The market size is $50 billion" in prompt
        assert "Verify the numerical claim" in prompt
        assert '"status"' in prompt  # asks for JSON output


# ── Data model tests ──────────────────────────────────────────────────────────


class TestModels:
    def test_verification_task_to_dict(self):
        task = VerificationTask(
            claim="X is Y",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Check this",
            priority="high",
            source_text="Original text",
        )
        d = task.to_dict()
        assert d["claim"] == "X is Y"
        assert d["priority"] == "high"

    def test_verification_result_to_dict(self):
        task = VerificationTask(
            claim="test",
            taxonomy_category="reasoning_errors",
            subcategory="logical_fallacy",
            rubric="Check",
            priority="medium",
        )
        result = VerificationResult(
            task=task,
            status="confirmed",
            evidence="Found matching data",
            confidence=0.9,
            explanation="Checks out",
        )
        d = result.to_dict()
        assert d["status"] == "confirmed"
        assert d["confidence"] == 0.9

    def test_verdict_to_dict_counts(self):
        task = VerificationTask(
            claim="test",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Check",
            priority="high",
        )
        checks = [
            VerificationResult(task=task, status="confirmed", evidence="", confidence=0.9, explanation=""),
            VerificationResult(task=task, status="refuted", evidence="", confidence=0.8, explanation=""),
            VerificationResult(task=task, status="uncertain", evidence="", confidence=0.5, explanation=""),
        ]
        verdict = VerificationVerdict(
            overall_status="needs_revision",
            confidence=0.7,
            checks=checks,
            feedback="Fix stuff",
            failed_claims=["test"],
        )
        d = verdict.to_dict()
        assert d["total_checks"] == 3
        assert d["passed"] == 1
        assert d["failed"] == 1
        assert d["uncertain"] == 1


# ── JSON parsing tests ────────────────────────────────────────────────────────


class TestJsonParsing:
    def test_parse_direct_json(self):
        result = parse_json_response('{"status": "confirmed"}')
        assert result["status"] == "confirmed"

    def test_parse_fenced_json(self):
        result = parse_json_response('Some text\n```json\n{"status": "refuted"}\n```\nMore text')
        assert result["status"] == "refuted"

    def test_parse_json_with_preamble(self):
        result = parse_json_response('Here is my analysis:\n{"status": "uncertain", "confidence": 0.5}')
        assert result["status"] == "uncertain"

    def test_parse_json_array(self):
        result = parse_json_response('[{"claim": "test"}]')
        assert "items" in result
        assert result["items"][0]["claim"] == "test"

    def test_parse_invalid_raises(self):
        import pytest
        with pytest.raises(ValueError):
            parse_json_response("This has no JSON at all")


# ── Decomposer tests (mocked LLM) ────────────────────────────────────────────


class TestDecomposer:
    @patch("verification.decomposer.call_llm_json")
    def test_decompose_extracts_claims(self, mock_llm):
        mock_llm.return_value = {
            "items": [
                {
                    "claim": "The market is worth $50B",
                    "taxonomy_category": "information_errors",
                    "subcategory": "factual_hallucination",
                    "priority": "high",
                    "source_text": "The market is worth $50B globally",
                },
                {
                    "claim": "Company X was founded in 2020",
                    "taxonomy_category": "information_errors",
                    "subcategory": "outdated_information",
                    "priority": "medium",
                    "source_text": "Founded in 2020",
                },
            ]
        }

        from verification.decomposer import decompose

        tasks = decompose("Some agent output about markets")
        assert len(tasks) == 2
        assert tasks[0].claim == "The market is worth $50B"
        assert tasks[0].priority == "high"
        assert tasks[0].taxonomy_category == "information_errors"
        # Should have a rubric from taxonomy
        assert len(tasks[0].rubric) > 20

    @patch("verification.decomposer.call_llm_json")
    def test_decompose_handles_empty(self, mock_llm):
        mock_llm.return_value = {"items": []}

        from verification.decomposer import decompose

        tasks = decompose("Short output")
        assert tasks == []


# ── Verifier tests (mocked LLM) ──────────────────────────────────────────────


class TestVerifier:
    @patch("verification.verifier.call_llm_json")
    def test_verify_confirmed_claim(self, mock_llm):
        mock_llm.return_value = {
            "status": "confirmed",
            "evidence": "Multiple sources confirm this",
            "confidence": 0.95,
            "explanation": "The claim is accurate",
        }

        from verification.verifier import verify

        task = VerificationTask(
            claim="Water boils at 100°C at sea level",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Verify this factual claim",
            priority="high",
        )
        result = verify(task)
        assert result.status == "confirmed"
        assert result.confidence == 0.95

    @patch("verification.verifier.call_llm_json")
    def test_verify_refuted_claim(self, mock_llm):
        mock_llm.return_value = {
            "status": "refuted",
            "evidence": "The actual number is different",
            "confidence": 0.85,
            "explanation": "Incorrect figure",
        }

        from verification.verifier import verify

        task = VerificationTask(
            claim="The population is 500 million",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Verify this claim",
            priority="high",
        )
        result = verify(task)
        assert result.status == "refuted"
        assert result.confidence == 0.85

    @patch("verification.verifier.call_llm_json")
    def test_verify_handles_llm_failure(self, mock_llm):
        mock_llm.side_effect = RuntimeError("LLM unavailable")

        from verification.verifier import verify

        task = VerificationTask(
            claim="Some claim",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Verify",
            priority="medium",
        )
        result = verify(task)
        assert result.status == "uncertain"
        assert result.confidence == 0.0


# ── Judge tests (mocked LLM) ─────────────────────────────────────────────────


class TestJudge:
    def _make_result(self, status, confidence=0.8, priority="high"):
        task = VerificationTask(
            claim=f"Test claim ({status})",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Check",
            priority=priority,
        )
        return VerificationResult(
            task=task,
            status=status,
            evidence="Test evidence",
            confidence=confidence,
            explanation="Test explanation",
        )

    def test_all_confirmed_passes_without_llm(self):
        from verification.judge import evaluate

        results = [
            self._make_result("confirmed", 0.9),
            self._make_result("confirmed", 0.85),
        ]
        verdict = evaluate(results, "test output")
        assert verdict.overall_status == "pass"
        assert verdict.confidence > 0.8
        assert len(verdict.failed_claims) == 0

    def test_empty_results_passes(self):
        from verification.judge import evaluate

        verdict = evaluate([], "test output")
        assert verdict.overall_status == "pass"
        assert verdict.confidence == 1.0

    @patch("verification.judge.call_llm_json")
    def test_mixed_results_needs_revision(self, mock_llm):
        mock_llm.return_value = {
            "overall_status": "needs_revision",
            "confidence": 0.6,
            "feedback": "Claim about population needs correction",
            "reasoning": "One claim refuted",
        }

        from verification.judge import evaluate

        results = [
            self._make_result("confirmed", 0.9),
            self._make_result("refuted", 0.8),
        ]
        verdict = evaluate(results, "test output")
        assert verdict.overall_status == "needs_revision"
        assert len(verdict.failed_claims) == 1

    @patch("verification.judge.call_llm_json")
    def test_fallback_on_llm_failure(self, mock_llm):
        mock_llm.side_effect = RuntimeError("LLM down")

        from verification.judge import evaluate

        results = [
            self._make_result("confirmed", 0.9),
            self._make_result("refuted", 0.8, priority="high"),
        ]
        verdict = evaluate(results, "test output")
        # Fallback should detect high-priority refutation
        assert verdict.overall_status == "fail"
        assert len(verdict.failed_claims) == 1


# ── Pipeline tests (mocked) ──────────────────────────────────────────────────


class TestPipeline:
    @patch("verification.pipeline.judge")
    @patch("verification.pipeline.verifier")
    @patch("verification.pipeline.decomposer")
    def test_full_pipeline_pass(self, mock_decomp, mock_verifier, mock_judge):
        task = VerificationTask(
            claim="Test",
            taxonomy_category="information_errors",
            subcategory="factual_hallucination",
            rubric="Check",
            priority="high",
        )
        result = VerificationResult(
            task=task,
            status="confirmed",
            evidence="OK",
            confidence=0.9,
            explanation="Good",
        )
        verdict = VerificationVerdict(
            overall_status="pass",
            confidence=0.9,
            checks=[result],
            feedback=None,
            failed_claims=[],
        )

        mock_decomp.decompose.return_value = [task]
        mock_verifier.verify.return_value = result
        mock_judge.evaluate.return_value = verdict

        from verification.pipeline import verify_output

        config = VerificationConfig(
            enabled=True,
            policy="thorough",
            parallel=False,
            log_results=False,
        )
        v = verify_output("Some agent output", config=config)
        assert v.overall_status == "pass"
        mock_decomp.decompose.assert_called_once()
        mock_verifier.verify.assert_called_once()
        mock_judge.evaluate.assert_called_once()

    @patch("verification.pipeline.decomposer")
    def test_pipeline_empty_decomposition(self, mock_decomp):
        mock_decomp.decompose.return_value = []

        from verification.pipeline import verify_output

        config = VerificationConfig(enabled=True, log_results=False)
        v = verify_output("Short output", config=config)
        assert v.overall_status == "pass"

    @patch("verification.pipeline.judge")
    @patch("verification.pipeline.verifier")
    @patch("verification.pipeline.decomposer")
    def test_quick_policy_filters_low_priority(self, mock_decomp, mock_verifier, mock_judge):
        high_task = VerificationTask(
            claim="Important", taxonomy_category="info", subcategory="fact",
            rubric="Check", priority="high",
        )
        low_task = VerificationTask(
            claim="Minor", taxonomy_category="info", subcategory="fact",
            rubric="Check", priority="low",
        )
        mock_decomp.decompose.return_value = [high_task, low_task]
        mock_verifier.verify.return_value = VerificationResult(
            task=high_task, status="confirmed", evidence="OK",
            confidence=0.9, explanation="Good",
        )
        mock_judge.evaluate.return_value = VerificationVerdict(
            overall_status="pass", confidence=0.9,
            checks=[], feedback=None, failed_claims=[],
        )

        from verification.pipeline import verify_output

        config = VerificationConfig(
            enabled=True, policy="quick", parallel=False, log_results=False,
        )
        verify_output("Output", config=config)

        # Only the high-priority task should be verified
        assert mock_verifier.verify.call_count == 1


# ── Config tests ──────────────────────────────────────────────────────────────


class TestConfig:
    def test_default_config(self):
        # With no config file, should return defaults
        config = VerificationConfig()
        assert config.enabled is True
        assert config.policy == "thorough"
        assert config.max_rounds == 2
        assert config.parallel is True
        assert config.model is None
        assert config.fail_action == "warn"

    def test_config_to_from_values(self):
        config = VerificationConfig(
            enabled=False,
            policy="quick",
            model="local",
        )
        assert config.enabled is False
        assert config.policy == "quick"
        assert config.model == "local"


# ── Logging tests ─────────────────────────────────────────────────────────────


class TestLogging:
    def test_log_entry_structure(self, tmp_path):
        from verification.logging import log_verification_run, VERIFICATION_LOG
        import verification.logging as log_mod

        # Redirect log to tmp
        original_log = log_mod.VERIFICATION_LOG
        log_mod.VERIFICATION_LOG = tmp_path / "verification.jsonl"

        try:
            verdict = VerificationVerdict(
                overall_status="pass",
                confidence=0.9,
                checks=[],
                feedback=None,
                failed_claims=[],
            )
            entry = log_verification_run(
                task_id="test-task",
                mission="test-mission",
                agent_output="Test output text",
                verdict=verdict,
                wall_time=5.2,
                total_llm_calls=3,
                verification_model="claude",
            )

            assert entry["task_id"] == "test-task"
            assert entry["mission"] == "test-mission"
            assert entry["overall_verdict"] == "pass"
            assert entry["wall_time_seconds"] == 5.2
            assert entry["total_llm_calls"] == 3

            # Verify file was written
            lines = log_mod.VERIFICATION_LOG.read_text().strip().splitlines()
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["task_id"] == "test-task"
        finally:
            log_mod.VERIFICATION_LOG = original_log
