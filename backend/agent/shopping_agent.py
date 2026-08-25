from typing import Any, List, Optional

from openai import AsyncOpenAI

from agent.instructions import AGENT_INSTRUCTIONS
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

    for tool_step in range(max_tool_steps + 1):
        response = await openai_client.responses.create(
            model=config.OPENAI_MODEL,
            instructions=AGENT_INSTRUCTIONS,
            input=model_input,
            tools=TOOL_DEFINITIONS,
            parallel_tool_calls=False,
        )
        function_calls = _function_calls(response)

        if not function_calls:
            if response.output_text:
                return response.output_text
            raise RuntimeError("The model returned neither a final answer nor a tool call")

        if tool_step >= max_tool_steps:
            raise AgentToolStepLimitError(
                f"Agent exceeded the maximum of {max_tool_steps} tool steps"
            )

        model_input.extend(response.output)
        for function_call in function_calls:
            result = await execute_tool(function_call.name, function_call.arguments)
            model_input.append({
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": result,
            })

    raise AgentToolStepLimitError("Agent tool-step limit exceeded")
