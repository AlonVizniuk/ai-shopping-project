import json
import logging
from dataclasses import asdict
from unittest.mock import AsyncMock

import pytest

from agent.observability import log_event
from agent.shopping_agent import AgentToolStepLimitError
from evals import __main__ as eval_cli
from evals.cases import EvalCase, EvalStatus
from evals import runner


def _emit_completed_run(tools=(), run_id="run-1"):
    log_event("agent_run.started", run_id, model="test", max_tool_steps=3)
    for index, tool_name in enumerate(tools):
        log_event("model_call.started", run_id, model_step=index, model="test")
        log_event(
            "tool_call.started",
            run_id,
            model_step=index,
            tool_step=index,
            tool_name=tool_name,
            tool_call_id=f"call-{index}",
            argument_names=[],
        )
        log_event(
            "tool_call.completed",
            run_id,
            model_step=index,
            tool_step=index,
            tool_name=tool_name,
            tool_call_id=f"call-{index}",
            duration_ms=1.0,
            result_size_chars=2,
        )
    log_event("model_call.started", run_id, model_step=len(tools), model="test")
    log_event(
        "agent_run.completed",
        run_id,
        duration_ms=10.0,
        model_call_count=len(tools) + 1,
        tool_call_count=len(tools),
        usage_complete=True,
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        cached_input_tokens=0,
        reasoning_tokens=0,
        answer_length_chars=10,
    )


def _case(**overrides):
    values = {
        "case_id": "case",
        "category": "test",
        "prompt": "prompt-secret",
    }
    values.update(overrides)
    return EvalCase(**values)


@pytest.mark.asyncio
async def test_run_case_passes_with_required_tool(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run(tools=("search_products",))
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(
        required_tools=frozenset({"search_products"}),
        allowed_tools=frozenset({"search_products"}),
        min_tool_calls=1,
    ))

    assert result.status is EvalStatus.PASS
    assert result.selected_tools == ("search_products",)
    assert result.total_tokens == 15


@pytest.mark.asyncio
async def test_run_case_allows_a_valid_secondary_tool(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run(tools=("search_products", "check_inventory"))
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(
        required_tools=frozenset({"search_products"}),
        allowed_tools=frozenset({
            "search_products",
            "get_product_details",
            "check_inventory",
        }),
        min_tool_calls=1,
    ))

    assert result.status is EvalStatus.PASS


@pytest.mark.asyncio
async def test_run_case_reports_missing_required_tool(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run()
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(required_tools=frozenset({"search_products"})))

    assert result.status is EvalStatus.BEHAVIOR_FAIL
    assert any("missing required tools" in reason for reason in result.reasons)


@pytest.mark.asyncio
async def test_run_case_reports_forbidden_or_unexpected_tool(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run(tools=("search_products",))
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(
        allowed_tools=frozenset(),
        forbidden_tools=frozenset({"search_products"}),
        max_tool_calls=0,
    ))

    assert result.status is EvalStatus.BEHAVIOR_FAIL
    assert any("unexpected selected tools" in reason for reason in result.reasons)
    assert any("forbidden selected tools" in reason for reason in result.reasons)


@pytest.mark.asyncio
async def test_run_case_passes_no_tool_case(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run()
        return "I can help with the store."

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(
        allowed_tools=frozenset(),
        max_tool_calls=0,
    ))

    assert result.status is EvalStatus.PASS
    assert result.tool_call_count == 0


@pytest.mark.asyncio
async def test_run_case_reports_answer_pattern_failure(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run()
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(required_answer_patterns=(r"cannot",)))

    assert result.status is EvalStatus.BEHAVIOR_FAIL
    assert "a required answer behavior was not present" in result.reasons


@pytest.mark.asyncio
async def test_run_case_classifies_runtime_exception_as_infra_error(monkeypatch):
    monkeypatch.setattr(
        runner,
        "run_agent",
        AsyncMock(side_effect=RuntimeError("infrastructure-secret")),
    )

    result = await runner.run_case(_case())

    assert result.status is EvalStatus.INFRA_ERROR
    assert result.error_type == "RuntimeError"
    assert "infrastructure-secret" not in json.dumps(asdict(result))


@pytest.mark.asyncio
async def test_run_case_classifies_tool_step_limit_as_behavior_failure(monkeypatch):
    monkeypatch.setattr(
        runner,
        "run_agent",
        AsyncMock(side_effect=AgentToolStepLimitError("step limit")),
    )

    result = await runner.run_case(_case())

    assert result.status is EvalStatus.BEHAVIOR_FAIL
    assert result.error_type == "AgentToolStepLimitError"


@pytest.mark.asyncio
async def test_run_case_removes_temporary_logging_handler(monkeypatch):
    logger = logging.getLogger("shopping_agent")
    initial_handlers = list(logger.handlers)

    async def fake_run_agent(prompt):
        _emit_completed_run()
        return "A safe answer"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    await runner.run_case(_case())

    assert logger.handlers == initial_handlers


@pytest.mark.asyncio
async def test_eval_result_does_not_retain_sensitive_prompt_or_answer(monkeypatch):
    async def fake_run_agent(prompt):
        _emit_completed_run()
        return "answer-secret"

    monkeypatch.setattr(runner, "run_agent", fake_run_agent)
    result = await runner.run_case(_case(prompt="prompt-secret"))

    serialized_result = json.dumps(asdict(result))
    assert "prompt-secret" not in serialized_result
    assert "answer-secret" not in serialized_result


@pytest.mark.asyncio
async def test_live_eval_lifecycle_connects_runs_and_disconnects(monkeypatch):
    call_order = []

    async def fake_connect():
        call_order.append("connect")

    async def fake_run_cases(cases):
        call_order.append("run_cases")
        return []

    async def fake_disconnect():
        call_order.append("disconnect")

    monkeypatch.setattr(eval_cli.database, "connect", fake_connect)
    monkeypatch.setattr(eval_cli, "run_cases", fake_run_cases)
    monkeypatch.setattr(eval_cli.database, "disconnect", fake_disconnect)

    assert await eval_cli._run_live_cases(()) == []
    assert call_order == ["connect", "run_cases", "disconnect"]


@pytest.mark.asyncio
async def test_live_eval_lifecycle_disconnects_when_eval_raises(monkeypatch):
    call_order = []

    async def fake_connect():
        call_order.append("connect")

    async def fake_run_cases(cases):
        call_order.append("run_cases")
        raise RuntimeError("eval failed")

    async def fake_disconnect():
        call_order.append("disconnect")

    monkeypatch.setattr(eval_cli.database, "connect", fake_connect)
    monkeypatch.setattr(eval_cli, "run_cases", fake_run_cases)
    monkeypatch.setattr(eval_cli.database, "disconnect", fake_disconnect)

    with pytest.raises(RuntimeError, match="eval failed"):
        await eval_cli._run_live_cases(())

    assert call_order == ["connect", "run_cases", "disconnect"]
