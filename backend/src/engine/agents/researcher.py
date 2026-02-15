from enum import Enum

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from ..models.llm import llm
from ..prompts.research_prompt import get_research_prompt
from ..tools.ddgs import search


class ResourceType(str, Enum):
    article = "article"
    video = "video"
    tutorial = "tutorial"
    other = "other"


class Resource(BaseModel):
    resource_type: ResourceType
    link: str
    title: str


class ResearchReportFormat(BaseModel):
    """Custom response format for Research Report output."""

    module: str
    title: str
    content: str
    resources: list[Resource]


RESEARCH_PROMPT = get_research_prompt()

agent = create_deep_agent(
    name="researcher-agent",
    model=llm,
    tools=[search],
    system_prompt=RESEARCH_PROMPT,
    response_format=ToolStrategy(ResearchReportFormat),
)
researcher_agent = agent
