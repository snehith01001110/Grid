"""Decomposition agent — extracts claims from agent output and maps to taxonomy.

Takes a research agent's full output and:
1. Extracts key factual claims and reasoning steps
2. Maps each claim/step to the most relevant failure taxonomy category
3. Generates specific verification sub-questions for each claim
"""

from __future__ import annotations

import json

from verification.llm import call_llm_json
from verification.models import VerificationTask
from verification.taxonomy import FAILURE_TAXONOMY, get_rubric

# Build a compact taxonomy reference for the decomposition prompt
_TAXONOMY_REF = ""
for cat_name, cat_data in FAILURE_TAXONOMY.items():
    _TAXONOMY_REF += f"\n- {cat_name}: {cat_data['description']}\n"
    for sub_name, sub_data in cat_data["subcategories"].items():
        _TAXONOMY_REF += f"  - {sub_name}: {sub_data['description']}\n"

DECOMPOSE_PROMPT = """You are a verification decomposer. Your job is to extract verifiable claims and reasoning steps from agent output, and map each to a failure taxonomy category.

FAILURE TAXONOMY:
{taxonomy}

AGENT OUTPUT TO DECOMPOSE:
\"\"\"
{agent_output}
\"\"\"

Extract the key factual claims, reasoning steps, and conclusions from this output. For each, identify:
1. The specific claim or reasoning step
2. Which taxonomy category and subcategory it maps to (for the most likely failure mode)
3. How critical this check is (high/medium/low)

Focus on:
- Specific factual assertions (numbers, dates, names, statistics)
- Causal claims ("X causes Y", "because of Z")
- Conclusions or recommendations
- Claims that, if wrong, would invalidate the overall output

Output ONLY a JSON array (no other text):
[
  {{
    "claim": "The specific claim to verify",
    "taxonomy_category": "category_name",
    "subcategory": "subcategory_name",
    "priority": "high|medium|low",
    "source_text": "The original sentence from the output"
  }}
]

Extract 3-10 claims, prioritizing the most impactful ones. Do NOT extract trivial or obvious claims."""


def decompose(agent_output: str, model: str | None = None) -> list[VerificationTask]:
    """Decompose agent output into a list of verification tasks.

    Args:
        agent_output: The full text output from the agent.
        model: Which model to use for decomposition (None = default).

    Returns:
        List of VerificationTask objects ready for the verifier.
    """
    prompt = DECOMPOSE_PROMPT.format(
        taxonomy=_TAXONOMY_REF,
        agent_output=agent_output[:8000],  # truncate very long outputs
    )

    response = call_llm_json(prompt, model=model)

    # Handle both {"items": [...]} and direct [...] shapes
    items = response if isinstance(response, list) else response.get("items", [])
    if not isinstance(items, list):
        items = [items] if isinstance(items, dict) else []

    tasks = []
    for item in items:
        if not isinstance(item, dict):
            continue

        category = item.get("taxonomy_category", "information_errors")
        subcategory = item.get("subcategory", "factual_hallucination")

        # Look up the rubric from taxonomy; fall back to a generic one
        rubric = get_rubric(category, subcategory)
        if not rubric:
            rubric = (
                "Verify the following claim by searching for independent evidence. "
                "Determine whether it is accurate, inaccurate, or uncertain."
            )

        tasks.append(
            VerificationTask(
                claim=item.get("claim", ""),
                taxonomy_category=category,
                subcategory=subcategory,
                rubric=rubric,
                priority=item.get("priority", "medium"),
                source_text=item.get("source_text", ""),
            )
        )

    return tasks
