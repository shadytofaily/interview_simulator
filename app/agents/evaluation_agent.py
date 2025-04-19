from agents import Agent
from app.agents.tools.extract_situation import extract_situation
from app.agents.tools.extract_task import extract_task
from app.agents.tools.extract_action import extract_action
from app.agents.tools.extract_result import extract_result

from typing import Dict
from pydantic import BaseModel, ConfigDict


class STAROutput(BaseModel):
    Situation: str
    Task: str
    Action: str
    Result: str

    model_config = ConfigDict(extra="forbid")  # 🛡️ запрет дополнительных полей


# Используется только для валидации response из value_agent
class ValuesEvaluation(BaseModel):
    Профессионализм: str
    Сотрудничество: str
    Ответственность: str
    Проактивность: str
    Саморазвитие: str

    model_config = ConfigDict(extra="forbid")


# Полный результат — не используется напрямую в агенте, но может быть полезен
class EvaluationResult(BaseModel):
    STAR: STAROutput
    Values: ValuesEvaluation

    model_config = ConfigDict(extra="forbid")


# Только основной агент STAR
def create_evaluation_agent(system_prompt: str) -> Agent:
    return Agent(
        name="Evaluation Agent",
        handoff_description="Оценка сообщений с использованием метода STAR.",
        instructions=system_prompt,
        tools=[extract_situation, extract_task, extract_action, extract_result],
        output_type=STAROutput
    )


# Генерация обратной связи по STAR
def generate_feedback(star_output: STAROutput, skill: str) -> str:
    feedback = []

    if not star_output.Situation or star_output.Situation.lower() in ["не указано", "не раскрыто"]:
        feedback.append("Не раскрыта ситуация, в которой происходило событие.")
    if not star_output.Task or "не" in star_output.Task.lower():
        feedback.append("Не указана конкретная задача или цель.")
    if not star_output.Action:
        feedback.append("Нет описания конкретных действий.")
    if not star_output.Result:
        feedback.append("Не указан результат или эффект.")

    if not feedback:
        return f"Ответ кандидата по компетенции '{skill}' хорошо структурирован и полностью покрывает метод STAR."

    return f"Ответ кандидата содержит пробелы по компетенции '{skill}':\n- " + "\n- ".join(feedback)
