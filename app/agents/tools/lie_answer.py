from typing import List

from agents import function_tool
from pydantic import BaseModel

from app.model.ttt import TTT

ttt = TTT()


class Message(BaseModel):
    role: str
    content: str


@function_tool
def lie_answer(messages: List[Message]) -> str:
    """
    Генерирует ложный ответ на основе персоны и проверяемого навыка.
    Ведет себя не естественно, смущается.
    Использует случайные элементы для разнообразия.

    Arguments:
        messages: Список сообщений для обработки.

    Return:
        response: Ответ.
    """
    response = ttt.generate_response_with_function(messages)
    return response
