from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from agent import shopping_agent


def response_with_tool_call(call_id="call-1", usage=None):
    call = SimpleNamespace(
        type="function_call",
        name="get_product_details",
        arguments='{"item_id": 1}',
        call_id=call_id,
    )
    return SimpleNamespace(
        id="resp-tool",
        status="completed",
        usage=usage,
        output=[call],
        output_text="",
    )


def final_response(text="The item is available.", usage=None):
    return SimpleNamespace(
        id="resp-final",
        status="completed",
        usage=usage,
        output=[],
        output_text=text,
    )


@pytest.mark.asyncio
async def test_agent_executes_one_tool_then_returns_final_response(monkeypatch):
    tool_call_response = response_with_tool_call()
    create = AsyncMock(side_effect=[tool_call_response, final_response()])
    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    execute_tool = AsyncMock(return_value='{"id": 1, "stock": 5}')
    monkeypatch.setattr(shopping_agent, "execute_tool", execute_tool)

    answer = await shopping_agent.run_agent(
        prompt="Tell me about item 1",
        client=client,
    )

    assert answer == "The item is available."
    execute_tool.assert_awaited_once_with(
        "get_product_details",
        '{"item_id": 1}',
    )
    assert create.await_count == 2

    second_input = create.await_args_list[1].kwargs["input"]
    assert second_input[0] == {
        "role": "user",
        "content": "Tell me about item 1",
    }
    assert second_input[1] is tool_call_response.output[0]
    assert second_input[2] == {
        "type": "function_call_output",
        "call_id": "call-1",
        "output": '{"id": 1, "stock": 5}',
    }


@pytest.mark.asyncio
async def test_agent_rejects_more_than_maximum_tool_steps(monkeypatch):
    create = AsyncMock(side_effect=[
        response_with_tool_call("call-1"),
        response_with_tool_call("call-2"),
        response_with_tool_call("call-3"),
    ])
    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    monkeypatch.setattr(
        shopping_agent,
        "execute_tool",
        AsyncMock(return_value="{}"),
    )

    with pytest.raises(shopping_agent.AgentToolStepLimitError):
        await shopping_agent.run_agent(
            prompt="Keep looking",
            client=client,
            max_tool_steps=2,
        )

    assert create.await_count == 3
