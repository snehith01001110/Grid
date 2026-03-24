#!/usr/bin/env python3
"""CLI entry point for the verification pipeline.

Called by mission.sh after task completion:
    echo "$output" | python3 verify.py [--task-id ID] [--mission NAME] [--model MODEL]

Exit codes:
    0 = pass (verification succeeded)
    1 = fail (critical claims refuted)
    2 = needs_revision (mixed or uncertain results)
    3 = error (pipeline failed)

Outputs JSON verdict to stdout, human-readable summary to stderr.
"""

import json
import sys
import os

# Ensure the Grid directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verification.config import VerificationConfig, load_config
from verification.pipeline import verify_output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DeepVerifier verification pipeline")
    parser.add_argument("--task-id", default="", help="Task identifier")
    parser.add_argument("--mission", default="", help="Mission name")
    parser.add_argument("--model", default=None, help="Override verification model")
    parser.add_argument("--policy", default=None, help="Override policy (quick|thorough|critical)")
    parser.add_argument("--max-rounds", type=int, default=None, help="Override max retry rounds")
    parser.add_argument("--output-file", default=None, help="Read agent output from file instead of stdin")
    parser.add_argument("--json", action="store_true", help="Output full JSON verdict")
    parser.add_argument("--init-config", action="store_true", help="Write default verification.conf and exit")
    args = parser.parse_args()

    if args.init_config:
        from verification.config import write_default_config
        write_default_config()
        print("Wrote default config to .mission/verification.conf", file=sys.stderr)
        sys.exit(0)

    # Load config with CLI overrides
    config = load_config()
    if args.model is not None:
        config.model = args.model or None
    if args.policy is not None:
        config.policy = args.policy
    if args.max_rounds is not None:
        config.max_rounds = args.max_rounds

    if not config.enabled:
        # Verification disabled — pass through silently
        sys.exit(0)

    # Read agent output
    if args.output_file:
        with open(args.output_file) as f:
            agent_output = f.read()
    elif not sys.stdin.isatty():
        agent_output = sys.stdin.read()
    else:
        print("Error: no agent output provided (pipe via stdin or use --output-file)", file=sys.stderr)
        sys.exit(3)

    if not agent_output.strip():
        print("Error: empty agent output", file=sys.stderr)
        sys.exit(3)

    # Run verification (with retries via feedback if configured)
    try:
        verdict = verify_output(
            agent_output=agent_output,
            task_id=args.task_id,
            mission=args.mission,
            config=config,
        )
    except Exception as e:
        print(f"Verification error: {e}", file=sys.stderr)
        sys.exit(3)

    # Output
    verdict_dict = verdict.to_dict()

    if args.json:
        print(json.dumps(verdict_dict, indent=2))
    else:
        # Human-readable summary to stderr, minimal JSON to stdout
        total = verdict_dict["total_checks"]
        passed = verdict_dict["passed"]
        failed = verdict_dict["failed"]
        uncertain = verdict_dict["uncertain"]

        status_icon = {"pass": "✓", "fail": "✗", "needs_revision": "⚠"}.get(
            verdict.overall_status, "?"
        )
        print(
            f"  {status_icon} Verification: {verdict.overall_status} "
            f"(confidence: {verdict.confidence:.0%}, "
            f"checks: {passed}✓ {failed}✗ {uncertain}? / {total})",
            file=sys.stderr,
        )

        if verdict.failed_claims:
            print("  Failed claims:", file=sys.stderr)
            for claim in verdict.failed_claims:
                print(f"    - {claim[:100]}", file=sys.stderr)

        if verdict.feedback:
            print(f"  Feedback: {verdict.feedback[:200]}", file=sys.stderr)

        # Stdout: compact JSON for mission.sh to parse
        print(json.dumps({
            "status": verdict.overall_status,
            "confidence": verdict.confidence,
            "feedback": verdict.feedback,
        }))

    # Exit code
    if verdict.overall_status == "pass":
        sys.exit(0)
    elif verdict.overall_status == "fail":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
