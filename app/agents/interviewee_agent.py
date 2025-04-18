from agents import Agent

from app.agents.tools.lie_answer import lie_answer
from app.model.ttt import TTT

ttt = TTT()  # Используется для форматирования истории в формат chat


class IntervieweeAgent:
    def __init__(self, system_prompt: str):
        self.base_agent = Agent(
            name="Агент кандидата на работу",
            handoff_description="Ты кандидат, который отвечает на вопросы на основе персоны и проверяемого навыка",
            instructions=system_prompt,
            tools=[lie_answer],
        )
        self.history = [{"role": "system", "content": system_prompt}]

    def append_to_history(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_messages(self):
        return [
            ttt.create_chat_message(msg["role"], msg["content"]) for msg in self.history
        ]

    def get_agent(self):
        return self.base_agent


def create_interviewee_agent(system_prompt: str) -> IntervieweeAgent:
    return IntervieweeAgent(system_prompt)
