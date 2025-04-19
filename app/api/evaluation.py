from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agents import Runner
from app.agents.evaluation_agent import create_evaluation_agent, STAROutput
from app.agents.value_agent import create_value_agent, ValueEvaluation

from app.agents.interviewer_feedback_agent import create_interviewer_feedback_agent, InterviewerFeedback


router = APIRouter()
templates = Jinja2Templates(directory="app/frontend")

# Загружаем системный промпт
from app.agents.prompts.utils import load_prompts
prompts = load_prompts("evaluation_system_prompt.yaml")
system_prompt = prompts["evaluation_system_prompt"]

interviewer_prompt = load_prompts("interviewer_feedback_prompt.yaml")
interviewer_prompt = interviewer_prompt["interviewer_feedback_prompt"]

# Хранилище последнего результата
last_evaluation_result = {}

@router.post("/api/evaluation")
async def evaluate_endpoint(request: Request):
    global last_evaluation_result

    # 1. Получаем входные данные
    data = await request.json()
    messages = data.get("messages", [])
    values = data.get("values", [])

    # 2. Загружаем системный промпт и создаём основной агент (оценка по STAR)
    system_prompt = prompts["evaluation_system_prompt"]
    agent = create_evaluation_agent(system_prompt)
    
    # 3. Запускаем основной агент
    star_run_result = await Runner.run(agent, messages)
    star_result: STAROutput = star_run_result.final_output_as(STAROutput)

    # 4. Оценка ценностей — если переданы
    values_result = {}

    if values:
        from app.agents.value_agent import create_value_agent  # импорт внутри, чтобы избежать циклов

        for value_name in values:
            prompt = f"Оцени ответ кандидата на соответствие ценности '{value_name}'. " \
                     f"Дай заключение (соответствует / не соответствует) и краткое пояснение."
            value_agent = create_value_agent(prompt)

            value_run_result = await Runner.run(value_agent, messages)
            value_evaluation = value_run_result.final_output_as(ValueEvaluation)

            values_result[value_name] = {
                "conclusion": value_evaluation.conclusion,
                "explanation": value_evaluation.explanation
            }

    # 4/5. Обратная связь по интервьюеру
    feedback_agent = create_interviewer_feedback_agent(interviewer_prompt)
    feedback_run_result = await Runner.run(feedback_agent, messages)
    feedback_result: InterviewerFeedback = feedback_run_result.final_output_as(InterviewerFeedback)


    # 5. Финальный результат
    last_evaluation_result = {
        "STAR": star_result.model_dump(),
        "Values": values_result,
        "InterviewerFeedback": feedback_result.model_dump()
    }

    return last_evaluation_result

@router.get("/api/evaluation")
async def get_evaluation_result():
    return last_evaluation_result

@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse("report.html", {
        "request": request,
        "result": last_evaluation_result
    })
