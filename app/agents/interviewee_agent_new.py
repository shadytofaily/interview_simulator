from agents import Agent
from app.agents.tools.lie_answer import lie_answer
from app.agents.tools.ask_hr_question import ask_hr_question
from app.agents.prompt_builder import render_persona_prompt

from agents import Agent
from app.agents.tools.lie_answer import lie_answer
from app.agents.tools.ask_hr_question import ask_hr_question
from app.agents.tools.debug_tool import summarize_last_user_question
from app.agents.prompt_builder import render_persona_prompt

def create_interviewee_agent(persona: str, skill: str) -> Agent:
    instructions = render_persona_prompt(persona, skill)

    return Agent(
        name=persona,
        handoff_description="Ты кандидат, отвечающий в заданной манере",
        instructions=instructions,
        tools=[
            lie_answer,
            ask_hr_question,
            summarize_last_user_question  # ← вот он
        ]
    )



def _inject_context_info(input, context):
    history = context.get("chat_history", [])
    if history:
        last_user_message = next(
            (m["content"] for m in reversed(history[:-1]) if m["role"] == "user"), None
        )
        if last_user_message:
            return f"{input}\n\n(Предыдущий вопрос был: '{last_user_message[:100]}')"
    return input

