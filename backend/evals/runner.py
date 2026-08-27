import json
import logging
import re
from typing import Iterable, List, Optional, Sequence, Tuple

from agent.shopping_agent import AgentToolStepLimitError, run_agent
from evals.cases import EvalCase, EvalResult, EvalStatus


class EventCaptureHandler(logging.Handler):
    """Temporarily collects structured agent events without changing logging setup."""

    def __init__(self) -> None:
        super().__init__()
        self.events: List[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            event = json.loads(record.getMessage())
            if isinstance(event, dict):
                self.events.append(event)
        except Exception:
            return


async def run_case(case: EvalCase) -> EvalResult:
    logger = logging.getLogger("shopping_agent")
    handler = EventCaptureHandler()
    logger.addHandler(handler)

    try:
        answer = await run_agent(prompt=case.prompt)
    except AgentToolStepLimitError as exc:
        return _result_from_events(
            case,
            handler.events,
            status=EvalStatus.BEHAVIOR_FAIL,
            reasons=["agent exceeded the maximum tool-step limit"],
            error_type=type(exc).__name__,
        )
    except Exception as exc:
        return _result_from_events(
            case,
            handler.events,
            status=EvalStatus.INFRA_ERROR,
            reasons=["agent execution did not complete"],
            error_type=type(exc).__name__,
        )
    finally:
        logger.removeHandler(handler)

    return _evaluate_completed_run(case, answer, handler.events)


async def run_cases(cases: Iterable[EvalCase]) -> List[EvalResult]:
    return [await run_case(case) for case in cases]


def _evaluate_completed_run(
    case: EvalCase,
    answer: str,
    events: Sequence[dict],
) -> EvalResult:
    completed_event = _last_event(events, "agent_run.completed")
    if completed_event is None:
        return _result_from_events(
            case,
            events,
            status=EvalStatus.INFRA_ERROR,
            reasons=["agent completion event was not captured"],
        )

    reasons = _behavior_reasons(case, answer, events)
    status = EvalStatus.PASS if not reasons else EvalStatus.BEHAVIOR_FAIL
    return _result_from_events(case, events, status=status, reasons=reasons)


def _behavior_reasons(
    case: EvalCase,
    answer: str,
    events: Sequence[dict],
) -> List[str]:
    selected_tools = set(_selected_tools(events))
    tool_call_count = len(_tool_events(events))
    reasons: List[str] = []

    missing_tools = case.required_tools - selected_tools
    if missing_tools:
        reasons.append("missing required tools: " + ", ".join(sorted(missing_tools)))

    if case.allowed_tools is not None:
        unexpected_tools = selected_tools - case.allowed_tools
        if unexpected_tools:
            reasons.append(
                "unexpected selected tools: " + ", ".join(sorted(unexpected_tools))
            )

    forbidden_tools = selected_tools & case.forbidden_tools
    if forbidden_tools:
        reasons.append(
            "forbidden selected tools: " + ", ".join(sorted(forbidden_tools))
        )

    if case.min_tool_calls is not None and tool_call_count < case.min_tool_calls:
        reasons.append("tool call count is below the required minimum")

    if case.max_tool_calls is not None and tool_call_count > case.max_tool_calls:
        reasons.append("tool call count exceeds the allowed maximum")

    for pattern in case.required_answer_patterns:
        if not re.search(pattern, answer, flags=re.IGNORECASE):
            reasons.append("a required answer behavior was not present")

    for pattern in case.forbidden_answer_patterns:
        if re.search(pattern, answer, flags=re.IGNORECASE):
            reasons.append("a forbidden answer behavior was present")

    return reasons


def _result_from_events(
    case: EvalCase,
    events: Sequence[dict],
    status: EvalStatus,
    reasons: List[str],
    error_type: Optional[str] = None,
) -> EvalResult:
    run_event = _last_event(events, "agent_run.completed")
    if run_event is None:
        run_event = _last_event(events, "agent_run.failed")
    run_id_event = _last_event(events, "agent_run.started")

    return EvalResult(
        case_id=case.case_id,
        category=case.category,
        status=status,
        reasons=reasons,
        run_id=(run_event or run_id_event or {}).get("run_id"),
        selected_tools=_selected_tools(events),
        model_call_count=len(_events_named(events, "model_call.started")),
        tool_call_count=len(_tool_events(events)),
        duration_ms=(run_event or {}).get("duration_ms"),
        input_tokens=(run_event or {}).get("input_tokens"),
        output_tokens=(run_event or {}).get("output_tokens"),
        total_tokens=(run_event or {}).get("total_tokens"),
        cached_input_tokens=(run_event or {}).get("cached_input_tokens"),
        reasoning_tokens=(run_event or {}).get("reasoning_tokens"),
        usage_complete=(run_event or {}).get("usage_complete"),
        error_type=error_type,
    )


def _events_named(events: Sequence[dict], event_name: str) -> List[dict]:
    return [event for event in events if event.get("event") == event_name]


def _last_event(events: Sequence[dict], event_name: str) -> Optional[dict]:
    matching_events = _events_named(events, event_name)
    return matching_events[-1] if matching_events else None


def _tool_events(events: Sequence[dict]) -> List[dict]:
    return _events_named(events, "tool_call.started")


def _selected_tools(events: Sequence[dict]) -> Tuple[str, ...]:
    return tuple(
        event["tool_name"]
        for event in _tool_events(events)
        if isinstance(event.get("tool_name"), str)
    )
