from agent.shopping_agent import AgentToolStepLimitError, run_agent
from exceptions.exception import chat_limit_exception

user_prompt_counter = {}


async def ask_assistant(user_id: int, prompt: str):
    current_count = user_prompt_counter.get(user_id, 0)

    if current_count >= 5:
        raise chat_limit_exception()

    user_prompt_counter[user_id] = current_count + 1

    try:
        assistant_answer = await run_agent(prompt=prompt)
    except AgentToolStepLimitError:
        assistant_answer = (
            "I couldn't complete that request within the allowed number of "
            "product lookups. Please try a more specific question."
        )

    return {
        "answer": assistant_answer,
        "prompts_left": 5 - user_prompt_counter[user_id]
    }


async def reset_chat(user_id: int):
    user_prompt_counter[user_id] = 0
    return {
        "message": "Chat reset successfully",
        "prompts_left": 5
    }
