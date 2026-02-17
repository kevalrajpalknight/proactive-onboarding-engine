from __future__ import annotations

from typing import List, Literal
from uuid import uuid4

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from ..models.llm import llm
from ..prompts.roadmap_prompt import get_roadmap_prompt

# ---------------------------------------------------------------------------
# Pydantic response models (no `id` or `status` — added in post-processing)
# ---------------------------------------------------------------------------


class RoadmapTopicFormat(BaseModel):
    """A single learning topic within a section."""

    title: str
    description: str
    estimatedDuration: str
    links: List[str]


class RoadmapSectionFormat(BaseModel):
    """A major section / milestone of the roadmap."""

    title: str
    description: str
    topics: List[RoadmapTopicFormat]


class CourseRoadmapFormat(BaseModel):
    """Structured output for a complete course roadmap."""

    title: str
    objective: str
    description: str
    level: Literal["beginner", "intermediate", "advanced"]
    totalEstimatedDuration: str
    sections: List[RoadmapSectionFormat]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

ROADMAP_PROMPT = get_roadmap_prompt()

roadmap_creator_agent = create_deep_agent(
    name="roadmap-creator",
    model=llm,
    system_prompt=ROADMAP_PROMPT,
    response_format=ToolStrategy(CourseRoadmapFormat),
)


# ---------------------------------------------------------------------------
# Post-processing: add UUIDs and default topic statuses
# ---------------------------------------------------------------------------


def post_process_roadmap(data: dict) -> dict:
    """Assign UUIDs and default statuses to a raw roadmap dict.

    The agent output does not include ``id`` or ``status`` fields.
    This function enriches the dict so it matches the frontend
    ``CourseRoadmap`` TypeScript interface exactly.

    Parameters
    ----------
    data:
        The dict produced by ``get_structured_output_parser`` on the
        roadmap creator agent's result.

    Returns
    -------
    dict
        A fully-formed ``CourseRoadmap`` payload ready for the frontend.
    """
    data["id"] = str(uuid4())

    for section in data.get("sections", []):
        section["id"] = str(uuid4())
        for topic in section.get("topics", []):
            topic["id"] = str(uuid4())
            topic.setdefault("status", "not_started")

    return data
