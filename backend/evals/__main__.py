import argparse
import asyncio
from collections import Counter
from typing import Optional, Sequence

from config.database import database
from evals.cases import EVAL_CASES, EvalResult, EvalStatus
from evals.runner import run_cases


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run live shopping-agent behavioral evals.")
    parser.add_argument("--case", dest="case_id", help="Run one eval case by ID.")
    args = parser.parse_args(argv)

    cases = EVAL_CASES
    if args.case_id:
        cases = tuple(case for case in EVAL_CASES if case.case_id == args.case_id)
        if not cases:
            parser.error("unknown eval case ID")

    results = asyncio.run(_run_live_cases(cases))
    for result in results:
        _print_result(result)

    summary = Counter(result.status for result in results)
    print(
        "SUMMARY "
        f"total={len(results)} "
        f"pass={summary[EvalStatus.PASS]} "
        f"behavior_fail={summary[EvalStatus.BEHAVIOR_FAIL]} "
        f"infra_error={summary[EvalStatus.INFRA_ERROR]}"
    )
    return 0 if all(result.status is EvalStatus.PASS for result in results) else 1


async def _run_live_cases(cases):
    await database.connect()
    try:
        return await run_cases(cases)
    finally:
        await database.disconnect()


def _print_result(result: EvalResult) -> None:
    tools = ",".join(result.selected_tools) if result.selected_tools else "none"
    parts = [
        result.status.value,
        result.case_id,
        f"tools={tools}",
        f"model_calls={result.model_call_count}",
        f"tool_calls={result.tool_call_count}",
    ]
    if result.error_type:
        parts.append(f"error_type={result.error_type}")
    if result.reasons:
        parts.append("reasons=" + " | ".join(result.reasons))
    print(" ".join(parts))


if __name__ == "__main__":
    raise SystemExit(main())
