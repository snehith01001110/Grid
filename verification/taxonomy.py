"""Failure taxonomy and rubric generation for verification.

Defines structured failure categories and maps each to executable
verification rubric prompts.
"""

from __future__ import annotations

FAILURE_TAXONOMY = {
    "reasoning_errors": {
        "description": "Logical or analytical mistakes in the agent's reasoning chain",
        "subcategories": {
            "logical_fallacy": {
                "description": "Invalid logical inference or contradiction between steps",
                "rubric": (
                    "Examine the following claim for logical validity. "
                    "Check for contradictions, non-sequiturs, circular reasoning, "
                    "or invalid inferences. State whether the logic holds."
                ),
            },
            "numerical_error": {
                "description": "Arithmetic, unit conversion, or quantitative mistakes",
                "rubric": (
                    "Verify all numbers, calculations, unit conversions, and "
                    "quantitative claims in the following statement. Recompute "
                    "any arithmetic independently. Flag any numerical errors."
                ),
            },
            "causal_confusion": {
                "description": "Incorrectly attributing cause-effect relationships",
                "rubric": (
                    "Analyze the cause-and-effect relationships claimed below. "
                    "Determine whether the causal attribution is justified by "
                    "evidence or if correlation is being mistaken for causation."
                ),
            },
        },
    },
    "decomposition_failures": {
        "description": "Errors in how the agent broke down the original task",
        "subcategories": {
            "incomplete_decomposition": {
                "description": "Missing critical sub-questions needed to answer fully",
                "rubric": (
                    "Given the original question and the agent's approach, identify "
                    "whether any critical sub-questions were missed that would be "
                    "necessary for a complete answer."
                ),
            },
            "irrelevant_subtask": {
                "description": "Pursuing sub-questions that don't contribute to the answer",
                "rubric": (
                    "Evaluate whether the following reasoning step or sub-task "
                    "is relevant to answering the original question. Flag if it "
                    "does not contribute to the final answer."
                ),
            },
            "scope_drift": {
                "description": "Gradually shifting away from the original question's intent",
                "rubric": (
                    "Compare the following claim or conclusion against the original "
                    "question. Determine if the agent has drifted from the intended "
                    "scope of the inquiry."
                ),
            },
        },
    },
    "action_errors": {
        "description": "Mistakes in tool usage or action selection",
        "subcategories": {
            "wrong_tool": {
                "description": "Using an inappropriate tool for the sub-task",
                "rubric": (
                    "Review the tool or action used for this step. Was the chosen "
                    "approach appropriate, or would a different tool or method "
                    "have been more suitable?"
                ),
            },
            "malformed_action": {
                "description": "Incorrectly formatted tool inputs or API calls",
                "rubric": (
                    "Check whether the tool invocation or action described below "
                    "was correctly formatted and would produce valid results."
                ),
            },
        },
    },
    "information_errors": {
        "description": "Problems with retrieved or synthesized information",
        "subcategories": {
            "factual_hallucination": {
                "description": "Stating facts not supported by any retrieved source",
                "rubric": (
                    "For the following factual claim, search for independent "
                    "evidence. Determine whether this fact can be verified from "
                    "reliable sources. Flag if the claim appears fabricated or "
                    "cannot be traced to any source."
                ),
            },
            "source_misinterpretation": {
                "description": "Correctly retrieving but incorrectly interpreting information",
                "rubric": (
                    "The agent retrieved information and drew the following "
                    "conclusion. Verify whether the interpretation accurately "
                    "reflects what the source material actually states."
                ),
            },
            "outdated_information": {
                "description": "Using information that is no longer current",
                "rubric": (
                    "Check whether the following claim relies on information "
                    "that may be outdated. Search for the most current data "
                    "and flag if the claim is no longer accurate."
                ),
            },
            "missing_citation": {
                "description": "Making claims without traceable source attribution",
                "rubric": (
                    "Evaluate whether the following claim has adequate source "
                    "attribution. If it makes specific factual assertions, "
                    "verify that sources are cited or traceable."
                ),
            },
        },
    },
    "cascading_failures": {
        "description": "Systemic failures that compound across steps",
        "subcategories": {
            "error_propagation": {
                "description": "Early mistake corrupting all downstream reasoning",
                "rubric": (
                    "Trace the reasoning chain leading to this claim. Identify "
                    "whether any upstream assumptions or facts are incorrect "
                    "and whether errors have propagated to this conclusion."
                ),
            },
        },
    },
}


def get_rubric(category: str, subcategory: str) -> str:
    """Return the rubric prompt for a given taxonomy category and subcategory."""
    cat = FAILURE_TAXONOMY.get(category, {})
    sub = cat.get("subcategories", {}).get(subcategory, {})
    return sub.get("rubric", "")


def get_all_categories() -> list[tuple[str, str, str, str]]:
    """Return flat list of (category, subcategory, description, rubric) tuples."""
    result = []
    for cat_name, cat_data in FAILURE_TAXONOMY.items():
        for sub_name, sub_data in cat_data["subcategories"].items():
            result.append((
                cat_name,
                sub_name,
                sub_data["description"],
                sub_data["rubric"],
            ))
    return result


def build_verification_prompt(claim: str, rubric: str) -> str:
    """Build a full verification prompt from a claim and rubric."""
    return f"""{rubric}

Claim to verify:
\"{claim}\"

Respond with ONLY a JSON object (no other text):
{{
  "status": "confirmed" | "refuted" | "uncertain",
  "evidence": "What evidence you found for or against this claim",
  "confidence": 0.0 to 1.0,
  "explanation": "Brief explanation of your verdict"
}}"""
