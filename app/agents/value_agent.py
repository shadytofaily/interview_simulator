from agents import Agent
from app.agents.tools.lie_answer import lie_answer  # если захочешь использовать
from pydantic import BaseModel

class ValueEvaluation(BaseModel):
    conclusion: str  # соответствует / не соответствует
    explanation: str  # пояснение

def create_value_agent(system_prompt: str) -> Agent:
    return Agent(
        name="Value Agent",
        handoff_description="Оценивает ответ кандидата на соответствие корпоративной ценности",
        instructions=system_prompt,
        output_type=ValueEvaluation,
    )
