import io
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from agent import observability, shopping_agent


def _usage(input_tokens, output_tokens, cached_tokens=0, reasoning_tokens=0):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        input_tokens_details=SimpleNamespace(cached_tokens=cached_tokens),
        output_tokens_details=SimpleNamespace(reasoning_tokens=reasoning_tokens),
    )


def _tool_response(usage=None):
    call = SimpleNamespace(
        type="function_call",
        name="get_product_details",
        arguments='{"item_id": 1, "note": "tool-argument-secret"}',
        call_id="call-1",
    )
    return SimpleNamespace(
        id="resp-tool",
        status="completed",
        usage=usage,
        output=[call],
        output_text="",
    )


def _final_response(usage=None, text="final-answer-secret"):
    return SimpleNamespace(
        id="resp-final",
        status="completed",
        usage=usage,
        output=[],
        output_text=text,
    )


@pytest.fixture
def agent_log_stream(monkeypatch):
    stream = io.StringIO()
    handler = observability.configure_logger()
    monkeypatch.setattr(handler, "stream", stream)
    return stream


def _events(agent_log_stream):
    return [
        json.loads(line)
        for line in agent_log_stream.getvalue().splitlines()
        if line
    ]


def test_logger_has_one_json_console_handler():
    handlers = [
        handler
        for handler in observability.logger.handlers
        if handler.get_name() == "shopping_agent_json_console"
    ]

    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert handlers[0].formatter._fmt == "%(message)s"
    assert observability.logger.propagate is False


def test_configure_logger_does_not_duplicate_handler():
    first_handler = observability.configure_logger()
    second_handler = observability.configure_logger()
    handlers = [
        handler
        for handler in observability.logger.handlers
        if handler.get_name() == "shopping_agent_json_console"
    ]

    assert first_handler is second_handler
    assert handlers == [first_handler]


def test_log_event_emits_one_structured_json_object(agent_log_stream):

    observability.log_event("test.event", "run-1", count=2)

    lines = agent_log_stream.getvalue().splitlines()
    assert len(lines) == 1

    event = json.loads(lines[0])
    assert event["schema_version"] == 1
    assert event["event"] == "test.event"
    assert event["run_id"] == "run-1"
    assert event["count"] == 2
    assert event["timestamp"].endswith("Z")


def test_log_event_is_failure_isolated(monkeypatch):
    monkeypatch.setattr(
        observability.logger,
        "info",
        lambda _: (_ for _ in ()).throw(RuntimeError("logging failed")),
    )

    observability.log_event("test.event", "run-1")


def test_extract_usage_returns_available_values():
    values = observability.extract_usage(_final_response(_usage(10, 5, 2, 1)))

    assert values == {
        "usage_available": True,
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
        "cached_input_tokens": 2,
        "reasoning_tokens": 1,
    }


def test_extract_usage_handles_missing_or_invalid_usage():
    assert observability.extract_usage(SimpleNamespace()) == {
        "usage_available": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_tokens": 0,
    }
    assert observability.extract_usage(SimpleNamespace(usage=object()))["usage_available"] is False


@pytest.mark.parametrize("input_tokens", [None, "10", -1, True])
def test_extract_usage_rejects_malformed_core_token_values(input_tokens):
    response = _final_response(_usage(10, 5))
    response.usage.input_tokens = input_tokens

    assert observability.extract_usage(response) == {
        "usage_available": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_tokens": 0,
    }


def test_extract_argument_names_omits_values():
    names = observability.extract_argument_names(
        '{"item_id": 1, "secret": "do-not-log-this"}'
    )

    assert names == ["item_id", "secret"]
    assert "do-not-log-this" not in json.dumps(names)


@pytest.mark.asyncio
async def test_agent_events_are_correlated_and_usage_is_complete(
    monkeypatch,
    agent_log_stream,
):
    create = AsyncMock(side_effect=[
        _tool_response(_usage(10, 4, cached_tokens=1)),
        _final_response(_usage(20, 6, reasoning_tokens=2)),
    ])
    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    monkeypatch.setattr(shopping_agent, "execute_tool", AsyncMock(
        return_value='{"result":"tool-result-secret"}'
    ))
    timings = iter([0.0, 1.0, 1.5, 2.0, 2.25, 3.0, 3.5, 4.0])
    monkeypatch.setattr(shopping_agent.time, "perf_counter", lambda: next(timings))

    answer = await shopping_agent.run_agent(
        prompt="prompt-secret",
        client=client,
    )

    events = _events(agent_log_stream)
    assert answer == "final-answer-secret"
    assert [event["event"] for event in events] == [
        "agent_run.started",
        "model_call.started",
        "model_call.completed",
        "tool_call.started",
        "tool_call.completed",
        "model_call.started",
        "model_call.completed",
        "agent_run.completed",
    ]
    assert len({event["run_id"] for event in events}) == 1
    assert events[2]["duration_ms"] == 500.0
    assert events[4]["duration_ms"] == 250.0
    assert events[-1]["duration_ms"] == 4000.0
    assert events[-1]["usage_complete"] is True
    assert events[-1]["input_tokens"] == 30
    assert events[-1]["output_tokens"] == 10
    assert events[-1]["total_tokens"] == 40
    assert events[-1]["cached_input_tokens"] == 1
    assert events[-1]["reasoning_tokens"] == 2
    assert events[3]["model_step"] == 0
    assert events[3]["tool_step"] == 0

    serialized_events = "\n".join(json.dumps(event) for event in events)
    assert "prompt-secret" not in serialized_events
    assert "tool-argument-secret" not in serialized_events
    assert "tool-result-secret" not in serialized_events
    assert "final-answer-secret" not in serialized_events


@pytest.mark.asyncio
async def test_missing_usage_makes_run_total_incomplete(
    monkeypatch,
    agent_log_stream,
):
    create = AsyncMock(side_effect=[
        _tool_response(_usage(10, 4)),
        _final_response(),
    ])
    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    monkeypatch.setattr(shopping_agent, "execute_tool", AsyncMock(return_value="{}"))

    answer = await shopping_agent.run_agent(prompt="item 1", client=client)

    completed = _events(agent_log_stream)[-1]
    assert answer == "final-answer-secret"
    assert completed["event"] == "agent_run.completed"
    assert completed["usage_complete"] is False
    assert completed["input_tokens"] == 10
    assert completed["output_tokens"] == 4
    assert completed["total_tokens"] == 14


@pytest.mark.asyncio
async def test_model_failure_is_observed_and_reraised(
    monkeypatch,
    agent_log_stream,
):
    client = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(side_effect=RuntimeError("api failed")))
    )

    with pytest.raises(RuntimeError, match="api failed"):
        await shopping_agent.run_agent(prompt="item 1", client=client)

    events = _events(agent_log_stream)
    assert [event["event"] for event in events] == [
        "agent_run.started",
        "model_call.started",
        "model_call.failed",
        "agent_run.failed",
    ]
    assert events[-1]["error_type"] == "RuntimeError"
    assert events[-1]["usage_complete"] is False
    assert "api failed" not in json.dumps(events)


@pytest.mark.asyncio
async def test_tool_failure_is_observed_and_reraised(
    monkeypatch,
    agent_log_stream,
):
    client = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(return_value=_tool_response(_usage(5, 2))))
    )
    monkeypatch.setattr(
        shopping_agent,
        "execute_tool",
        AsyncMock(side_effect=ValueError("tool failed")),
    )

    with pytest.raises(ValueError, match="tool failed"):
        await shopping_agent.run_agent(prompt="item 1", client=client)

    events = _events(agent_log_stream)
    assert [event["event"] for event in events] == [
        "agent_run.started",
        "model_call.started",
        "model_call.completed",
        "tool_call.started",
        "tool_call.failed",
        "agent_run.failed",
    ]
    assert events[-1]["error_type"] == "ValueError"
    assert events[-1]["usage_complete"] is True
    assert "tool failed" not in json.dumps(events)
