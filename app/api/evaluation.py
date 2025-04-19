from fastapi import APIRouter, Request

from app.agents.evaluation_agent import create_evaluation_agent
from app.agents.dialogue_evaluation_agent import create_criteria_checker_agent

from agents import Runner

from app.agents.prompts.utils import load_prompts

router = APIRouter()

prompts = load_prompts("evaluation_system_prompt.yaml")
system_prompt = prompts["evaluation_system_prompt"]
criteria_system_promt = load_prompts("criteria_checker_prompt.yaml")["criteria_checker_prompt"]

# Хранилище для последних результатов оценки
last_evaluation_result:dict = {}

@router.post("/api/evaluation")
async def evaluate_endpoint(request: Request):
    global last_evaluation_result
    # 1. Считаем входные данные
    data = await request.json()
    messages = data.get("messages", [])
    # 2. Создадим агента с системным промптом
    agent = create_evaluation_agent(system_prompt)
    criteria_agent = create_criteria_checker_agent(criteria_system_promt)
    # 3. Получим ответ от агента
    response = await Runner.run(agent, messages)
    response_criteria = await Runner.run(criteria_agent, messages)
    # 4. Преобразуем в словарь и запомним
    last_evaluation_result = response.final_output_as(cls=dict)
    last_evaluation_result_ciriteria = response_criteria.final_output_as(cls=dict)
    # 5. Вернём клиенту результат сразу
    result = {'last_evaluation_result_ciriteria':last_evaluation_result_ciriteria, 'last_evaluation_result':last_evaluation_result}
    return result

@router.get("/api/evaluation")
async def get_evaluation_result():
    """Эндпоинт для получения последних результатов оценки."""
    return last_evaluation_result