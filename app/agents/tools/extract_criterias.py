from typing import List

from agents import function_tool
from pydantic import BaseModel

from app.model.ttt import TTT

ttt = TTT()


class Message(BaseModel):
    role: str
    content: str


extract_criterias_json = {
    "type": "function",
    "name": "extract_task",
    "description": """
                По тексту интервью попробуй ответить на вопросы из критериев оценки:
                - Насколько интервью было структурированным (была ли логика и последовательность)?
                - Было ли задано достаточное количество вопросов для полноценной проверки компетенций кандидата?
                - Корректно ли рекрутер завершил интервью (подведение итогов, вежливое закрытие диалога)?
                - Проинформировал ли рекрутер кандидата о дальнейших этапах процесса и ожиданиях?
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "Criteria": {
                "type": "string",
                "description": "Извлеченная задача из собеседования. Если задача не указана, не выдумывайте ее, просто укажите, что задача не описана.",
            }
        },
        "required": ["Criteria"],
        "additionalProperties": False,
    },
    "strict": True,
}


@function_tool
def extract_criterias(messages: List[Message]) -> str:
    """
    Ответить на вопросы соответствия собеседования определенным критериям. Не выдумывайте ничего, используйте только предоставленную информацию из собеседования и списка криетриев.

    Args:
        messages (list): Список сообщений из собеседования. Каждое сообщение - словарь, содержащий 'role' и 'content'.

    Return:
        str: Ответы на вопросы соответствия собеседования заданным криетриям.
    """

    response = ttt.generate_response_with_function(
        messages=messages,
        functions=[extract_criterias_json],
    )
    print("Response from extract_criteria:", response)
    return response
