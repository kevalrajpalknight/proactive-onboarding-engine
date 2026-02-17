"""RAG search tool – queries the ChromaDB company-policies collection.

This LangChain tool is designed to be used by agents that need to answer
questions about internal company policies (onboarding, leaves, code of
conduct, etc.).  Each result includes the source document filename so
the agent can cite it.
"""

from __future__ import annotations

import os
from functools import lru_cache

import chromadb
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------------------------
# Vectorstore singleton
# ---------------------------------------------------------------------------

_CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
_CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8100"))
_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "company_policies")


@lru_cache(maxsize=1)
def _get_vectorstore() -> Chroma:
    """Return a cached Chroma vectorstore client."""
    client = chromadb.HttpClient(host=_CHROMA_HOST, port=_CHROMA_PORT)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return Chroma(
        client=client,
        collection_name=_COLLECTION,
        embedding_function=embeddings,
    )


# ---------------------------------------------------------------------------
# LangChain Tool
# ---------------------------------------------------------------------------


@tool
def search_company_policies(query: str) -> str:
    """Search internal company policy documents for information.

    Use this tool when the user's question is about company policies,
    onboarding procedures, leave benefits, code of conduct, HR processes,
    or any other internal organisational topic.

    Args:
        query: A natural-language search query about company policies.

    Returns:
        Relevant policy excerpts with source citations.
    """
    vectorstore = _get_vectorstore()

    results = vectorstore.similarity_search_with_relevance_scores(
        query,
        k=5,
    )

    if not results:
        return "No relevant company policy documents found " "for the given query."

    formatted_results: list[str] = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        section = doc.metadata.get("section", "")
        citation = f"[Source: {source}]"
        if section:
            citation = f"[Source: {source} — {section}]"

        formatted_results.append(
            f"--- Result {i} (relevance: {score:.2f}) {citation} ---\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted_results)
