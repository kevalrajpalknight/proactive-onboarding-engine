"""Policy researcher agent — answers company policy questions via RAG.

This agent uses the ``search_company_policies`` tool to query the
ChromaDB vector store and synthesise answers grounded in internal
policy documents.  Every answer includes source citations.
"""

from __future__ import annotations

from deepagents import create_deep_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from ..models.llm import llm
from ..prompts.policy_prompt import get_policy_research_prompt
from ..tools.rag_search import search_company_policies

# ---------------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------------


class PolicySourceFormat(BaseModel):
    """A single cited source document."""

    document: str
    section: str
    relevance: str


class PolicyResearchFormat(BaseModel):
    """Structured output for a policy research answer."""

    query: str
    answer: str
    sources: list[PolicySourceFormat]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

POLICY_PROMPT = get_policy_research_prompt()

policy_researcher_agent = create_deep_agent(
    name="policy-researcher-agent",
    model=llm,
    tools=[search_company_policies],
    system_prompt=POLICY_PROMPT,
    response_format=ToolStrategy(PolicyResearchFormat),
)
