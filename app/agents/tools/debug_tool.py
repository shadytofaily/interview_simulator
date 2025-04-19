from typing import List
from pydantic import BaseModel
from agents import function_tool, RunContextWrapper

class Message(BaseModel):
    role: str
    content: str

@function_tool
async def summarize_last_user_question(ctx: RunContextWrapper[None]) -> str:
    history = ctx.context.get("chat_history", [])
    last_user_msg = next(
        (msg["content"] for msg in reversed(history) if msg.get("role") == "user"),
        None
    )
    if last_user_msg:
        return f"🧠 Предыдущий вопрос пользователя: '{last_user_msg[:100]}...'"
    else:
        return "🧠 Нет предыдущего вопроса в истории."
