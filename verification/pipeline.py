"""Pipeline orchestrator — ties decomposition, verification, and judging together.

This is the main entry point for running verification on agent output.
It coordinates the decomposer, verifier, and judge into a single flow.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from verification import decomposer, judge, verifier
from verification.config import VerificationConfig, load_config
from verification.logging import log_verification_run
from verification.models import VerificationResult, VerificationVerdict


def verify_output(
    agent_output: str,
    task_id: str = "",
    mission: str = "",
    config: VerificationConfig | None = None,
    verification_round: int = 1,
) -> VerificationVerdict:
    """Run the full verification pipeline on agent output.

    Args:
        agent_output: The agent's full text output to verify.
        task_id: Task identifier (for logging).
        mission: Mission name (for logging).
        config: Verification config (loads from file if None).
        verification_round: Which retry round this is.

    Returns:
        VerificationVerdict with overall status, confidence, and feedback.
    """
    if config is None:
        config = load_config()

    start_time = time.time()
    llm_calls = 0

    # Step 1: Decompose output into verification tasks
    tasks = decomposer.decompose(agent_output, model=config.model)
    llm_calls += 1

    if not tasks:
        # Nothing to verify — auto-pass
        verdict = VerificationVerdict(
            overall_status="pass",
            confidence=1.0,
            checks=[],
            feedback=None,
            failed_claims=[],
        )
        _log_if_enabled(
            config, task_id, mission, agent_output, verdict,
            time.time() - start_time, llm_calls, verification_round,
        )
        return verdict

    # Step 2: Filter/prioritize based on policy
    if config.policy == "quick":
        tasks = [t for t in tasks if t.priority == "high"]
    elif config.policy == "critical":
        pass  # keep all tasks, no filtering
    else:
        # "thorough" — keep high and medium
        tasks = [t for t in tasks if t.priority in ("high", "medium")]

    if not tasks:
        verdict = VerificationVerdict(
            overall_status="pass",
            confidence=1.0,
            checks=[],
            feedback=None,
            failed_claims=[],
        )
        _log_if_enabled(
            config, task_id, mission, agent_output, verdict,
            time.time() - start_time, llm_calls, verification_round,
        )
        return verdict

    # Step 3: Run verification tasks (parallel or sequential)
    results: list[VerificationResult] = []

    if config.parallel and len(tasks) > 1:
        with ThreadPoolExecutor(max_workers=config.max_workers) as pool:
            futures = {
                pool.submit(verifier.verify, task, config.model): task
                for task in tasks
            }
            for future in as_completed(futures):
                results.append(future.result())
                llm_calls += 1
    else:
        for task in tasks:
            results.append(verifier.verify(task, model=config.model))
            llm_calls += 1

    # Step 4: Judge the results
    verdict = judge.evaluate(results, agent_output, model=config.model)
    llm_calls += 1  # judge may make an LLM call

    # Step 5: Log
    wall_time = time.time() - start_time
    _log_if_enabled(
        config, task_id, mission, agent_output, verdict,
        wall_time, llm_calls, verification_round,
    )

    return verdict


def _log_if_enabled(
    config: VerificationConfig,
    task_id: str,
    mission: str,
    agent_output: str,
    verdict: VerificationVerdict,
    wall_time: float,
    llm_calls: int,
    verification_round: int,
) -> None:
    """Log the verification run if logging is enabled."""
    if config.log_results:
        log_verification_run(
            task_id=task_id,
            mission=mission,
            agent_output=agent_output,
            verdict=verdict,
            wall_time=wall_time,
            total_llm_calls=llm_calls,
            verification_model=config.model,
            verification_round=verification_round,
        )
