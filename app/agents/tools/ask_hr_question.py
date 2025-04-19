from app.model.ttt import TTT
from agents import function_tool  # ← корректный импорт
from typing import List
from pydantic import BaseModel
from pathlib import Path
import random
import yaml

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class Message(BaseModel):
    role: str
    content: str

@function_tool
def ask_hr_question(messages: List[Message]) -> str:
    """
    Кандидат задаёт вопрос HR-у о компании или условиях.
    Возвращает случайный вопрос из YAML.
    """
    path = PROMPTS_DIR / "candidate_questions.yaml"
    data = load_yaml(path)
    question = random.choice(data["questions"])
    return f"А теперь у меня вопрос к вам как к работодателю: {question}"
