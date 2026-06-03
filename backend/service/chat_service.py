from openai import OpenAI

from config.config import Config
from exceptions.exception import chat_limit_exception
from repository import item_repository

config = Config()

client = OpenAI(api_key=config.OPENAI_API_KEY)

user_prompt_counter = {}
user_messages = {}


async def ask_assistant(user_id: int, username: str, prompt: str):
    current_count = user_prompt_counter.get(user_id, 0)

    if current_count >= 5:
        raise chat_limit_exception()

    user_prompt_counter[user_id] = current_count + 1

    items = await item_repository.get_items()

    items_context = "\n".join([
        f"- {item['name']}, price: {item['price']}, stock: {item['stock']}"
        for item in items
    ])

    messages = [
        {
            "role": "system",
            "content": f"""
            You are an AI shopping assistant for a World Cup jersey store website.
            
            The current logged in user is: {username}
            You may address the user by their username naturally.
            
            Your role:
            - Help users understand the website.
            - Recommend jerseys.
            - Answer questions about products, stock, prices, favorites, orders, and shopping flow.
            - Help users navigate the website pages.

            Website pages and features:

            - Main Page:
            Users can search jerseys, filter by price and stock,
            add items to cart, and manage favorites.

            - Favorite Jerseys Page:
            Users can view favorite jerseys,
            remove favorites, and add favorite items to cart.

            - Order Page:
            Users can manage their pending order,
            update quantities,
            remove items,
            delete pending orders,
            purchase the order,
            and view closed orders history.

            - Chat Assistant Page:
            Users can ask questions about products,
            stock,
            prices,
            recommendations,
            and website usage.

            Important rules:
            - Only answer about the shopping website and its products.
            - If the user asks unrelated questions, politely refuse.
            - If stock is 0, the product is out of stock.
            - Be short, friendly, and helpful.
            - The user has {5 - user_prompt_counter[user_id]} prompts left after this message.

            Current store items:
            {items_context}
            """
        }
    ]

    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append({
        "role": "user",
        "content": prompt
    })

    messages.extend(user_messages[user_id])

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=messages
    )

    assistant_answer = response.choices[0].message.content

    user_messages[user_id].append({
        "role": "assistant",
        "content": assistant_answer
    })

    return {
        "answer": assistant_answer,
        "prompts_left": 5 - user_prompt_counter[user_id]
    }


async def reset_chat(user_id: int):
    user_prompt_counter[user_id] = 0
    user_messages[user_id] = []
    return {"message": "Chat reset successfully", "prompts_left": 5}