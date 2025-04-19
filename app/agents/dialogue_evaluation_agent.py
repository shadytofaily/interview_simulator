# app/agents/dialogue_evaluation_agent.py
from agents import Agent
from pydantic import BaseModel

# from app.agents.tools.extract_situation import extract_situation
# from app.agents.tools.extract_task import extract_task
# from app.agents.tools.extract_action import extract_action
# from app.agents.tools.extract_result import extract_result
from app.agents.tools.extract_criterias import extract_criterias


class CriteriaOutput(BaseModel):
    Situation: str
    Enough_questions: str
    Relevantly_ended: str
    Candidate_steps: str


def create_criteria_checker_agent(system_prompt: str) -> Agent:
    return Agent(
        name="Criteria checker Agent",
        handoff_description="Оценка работы HR специалиста по заданным критериям",
        instructions=system_prompt,
        tools=[extract_criterias],
        output_type=CriteriaOutput,
    )
