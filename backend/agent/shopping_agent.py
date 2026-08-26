import time
import uuid
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from agent.instructions import AGENT_INSTRUCTIONS
from agent.observability import extract_argument_names, extract_usage, log_event
from agent.tools import TOOL_DEFINITIONS, execute_tool
from config.config import Config


MAX_TOOL_STEPS = 3


class AgentToolStepLimitError(RuntimeError):
    pass


def _function_calls(response: Any) -> List[Any]:
    return [item for item in response.output if item.type == "function_call"]


async def run_agent(
    prompt: str,
    client: Optional[AsyncOpenAI] = None,
    max_tool_steps: int = MAX_TOOL_STEPS,
) -> str:
    config = Config()
    openai_client = client or AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    model_input: List[Any] = [{"role": "user", "content": prompt}]
    run_id = uuid.uuid4().hex
    run_started_at = time.perf_counter()
    model_call_count = 0
    tool_call_count = 0
    usage_complete = True
    usage_totals: Dict[str, int] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_tokens": 0,
    }

    log_event(
        "agent_run.started",
        run_id,
        model=config.OPENAI_MODEL,
        max_tool_steps=max_tool_steps,
        prompt_length_chars=len(prompt),
    )

    try:
        for model_step in range(max_tool_steps + 1):
            model_call_count += 1
            model_started_at = time.perf_counter()
            log_event(
                "model_call.started",
                run_id,
                model_step=model_step,
                model=config.OPENAI_MODEL,
                accumulated_input_items=len(model_input),
            )

            try:
                response = await openai_client.responses.create(
                    model=config.OPENAI_MODEL,
                    instructions=AGENT_INSTRUCTIONS,
                    input=model_input,
                    tools=TOOL_DEFINITIONS,
                    parallel_tool_calls=False,
                )
            except Exception as exc:
                usage_complete = False
                log_event(
                    "model_call.failed",
                    run_id,
                    model_step=model_step,
                    duration_ms=_duration_ms(model_started_at),
                    error_type=type(exc).__name__,
                )
                raise

            usage = extract_usage(response)
            if not usage["usage_available"]:
                usage_complete = False
            _add_usage(usage_totals, usage)

            function_calls = _function_calls(response)
            log_event(
                "model_call.completed",
                run_id,
                model_step=model_step,
                duration_ms=_duration_ms(model_started_at),
                response_id=getattr(response, "id", None),
                response_status=getattr(response, "status", None),
                function_call_count=len(function_calls),
                output_item_types=[
                    getattr(item, "type", "unknown") for item in response.output
                ],
                **usage,
            )

            if not function_calls:
                if response.output_text:
                    answer = response.output_text
                    log_event(
                        "agent_run.completed",
                        run_id,
                        duration_ms=_duration_ms(run_started_at),
                        model_call_count=model_call_count,
                        tool_call_count=tool_call_count,
                        usage_complete=usage_complete,
                        **usage_totals,
                        answer_length_chars=len(answer),
                    )
                    return answer
                raise RuntimeError(
                    "The model returned neither a final answer nor a tool call"
                )

            if model_step >= max_tool_steps:
                raise AgentToolStepLimitError(
                    f"Agent exceeded the maximum of {max_tool_steps} tool steps"
                )

            model_input.extend(response.output)
            for function_call in function_calls:
                tool_step = tool_call_count
                tool_call_count += 1
                tool_started_at = time.perf_counter()
                log_event(
                    "tool_call.started",
                    run_id,
                    model_step=model_step,
                    tool_step=tool_step,
                    tool_name=function_call.name,
                    tool_call_id=function_call.call_id,
                    argument_names=extract_argument_names(function_call.arguments),
                )

                try:
                    result = await execute_tool(
                        function_call.name,
                        function_call.arguments,
                    )
                except Exception as exc:
                    log_event(
                        "tool_call.failed",
                        run_id,
                        model_step=model_step,
                        tool_step=tool_step,
                        tool_name=function_call.name,
                        tool_call_id=function_call.call_id,
                        duration_ms=_duration_ms(tool_started_at),
                        error_type=type(exc).__name__,
                    )
                    raise

                log_event(
                    "tool_call.completed",
                    run_id,
                    model_step=model_step,
                    tool_step=tool_step,
                    tool_name=function_call.name,
                    tool_call_id=function_call.call_id,
                    duration_ms=_duration_ms(tool_started_at),
                    result_size_chars=len(result),
                )
                model_input.append({
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": result,
                })

        raise AgentToolStepLimitError("Agent tool-step limit exceeded")
    except Exception as exc:
        log_event(
            "agent_run.failed",
            run_id,
            duration_ms=_duration_ms(run_started_at),
            model_call_count=model_call_count,
            tool_call_count=tool_call_count,
            usage_complete=usage_complete,
            **usage_totals,
            error_type=type(exc).__name__,
        )
        raise


def _duration_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 2)


def _add_usage(usage_totals: Dict[str, int], usage: Dict[str, Any]) -> None:
    for field in usage_totals:
        usage_totals[field] += usage[field]
