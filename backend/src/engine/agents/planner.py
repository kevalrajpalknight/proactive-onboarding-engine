from enum import Enum

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from ..models.llm import llm
from ..prompts.planner_prompt import get_planner_prompt


class AgentType(str, Enum):
    internet_search_agent = "internet_search_agent"
    search_youtube_videos = "search_youtube_videos"


class ToDoListResponseFormat(BaseModel):
    """Custom response format for To-Do List output."""

    description: str
    agent: AgentType


PLANNER_PROMPT = get_planner_prompt()
print("Planner Prompt Loaded:", PLANNER_PROMPT)
agent = create_deep_agent(
    name="proactive-onboarding-engine",
    model=llm,
    system_prompt=PLANNER_PROMPT,
    response_format=ToolStrategy(ToDoListResponseFormat),
)
planner_agent = agent
