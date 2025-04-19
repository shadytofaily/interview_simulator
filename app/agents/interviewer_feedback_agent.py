from agents import Agent
from pydantic import BaseModel

class InterviewerFeedback(BaseModel):
    structure: str
    competency_coverage: str
    closing: str
    tone: str
    overall: str

def create_interviewer_feedback_agent(system_prompt: str) -> Agent:
    return Agent(
        name="Interviewer Feedback Agent",
        handoff_description="Оценивает, насколько хорошо интервьюер провел интервью",
        instructions=system_prompt,
        output_type=InterviewerFeedback,
    )
