"""Roadmap curation engine entrypoint.

This module exposes ``curate_roadmap`` which is designed to be run as a
background task (via ``asyncio.create_task`` or a task-queue worker).

It publishes progress updates to a Redis channel so that the WebSocket
layer can stream them to the connected client.  It also keeps a Redis
key with the latest state so that reconnecting clients can catch up.

The actual AI / LangGraph orchestration is left as a stub so that you
can wire it up to the planner + researcher agents incrementally.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog

from ..core.redis import get_redis, roadmap_channel, roadmap_state_key
from .agents import (
    planner_agent,
    policy_researcher_agent,
    post_process_roadmap,
    researcher_agent,
    roadmap_creator_agent,
)
from .utils.output_parser import get_structured_output_parser

logger = structlog.get_logger()

# Keep strong references to running tasks so they aren't GC'd
_running_tasks: set[asyncio.Task] = set()


def _serialize_agent_result(result: Any) -> Any:
    """Convert a LangGraph agent result into a JSON-serialisable dict.

    Agent ``.invoke()`` returns a dict whose ``"messages"`` value is a
    list of LangChain ``BaseMessage`` objects.  This helper converts
    each message to a plain dict so that downstream ``json.dumps``
    calls succeed.
    """
    if isinstance(result, dict):
        out: dict[str, Any] = {}
        for key, value in result.items():
            if key == "messages" and isinstance(value, list):
                out[key] = [
                    (
                        msg.dict()
                        if hasattr(msg, "dict")
                        else (
                            msg.model_dump() if hasattr(msg, "model_dump") else str(msg)
                        )
                    )
                    for msg in value
                ]
            elif key == "structured_response":
                if hasattr(value, "model_dump"):
                    out[key] = value.model_dump()
                elif hasattr(value, "dict"):
                    out[key] = value.dict()
                else:
                    out[key] = value
            else:
                out[key] = value
        return out
    return result


async def _publish_progress(
    session_id: str,
    *,
    status: str,
    step: str,
    detail: str = "",
    progress_pct: int = 0,
    roadmap: dict[str, Any] | None = None,
) -> None:
    """Publish a progress event to Redis (channel + state key).

    Parameters
    ----------
    session_id:
        The chat / roadmap session identifier.
    status:
        One of ``pending``, ``in_progress``, ``completed``, ``error``.
    step:
        A short machine-readable label for the current step,
        e.g. ``"analysing_answers"``, ``"generating_roadmap"``.
    detail:
        A human-readable description shown in the UI.
    progress_pct:
        Percentage (0-100) of overall progress.
    roadmap:
        When ``status == "completed"``, the full roadmap payload.
    """
    payload: dict[str, Any] = {
        "session_id": session_id,
        "status": status,
        "step": step,
        "detail": detail,
        "progress_pct": progress_pct,
    }
    if roadmap is not None:
        payload["roadmap"] = roadmap

    redis = get_redis()
    raw = json.dumps(payload)

    # Persist latest state for reconnection (TTL 1 hour)
    await redis.set(roadmap_state_key(session_id), raw, ex=3600)
    # Publish on the channel for real-time listeners
    await redis.publish(roadmap_channel(session_id), raw)


async def curate_roadmap(session_id: str, chat_data: dict[str, Any]) -> None:
    """Orchestrate roadmap curation and publish progress via Redis.

    This is the main entrypoint that should be called as a background
    task once the questionnaire is completed.

    Parameters
    ----------
    session_id:
        The UUID of the completed chat session.
    chat_data:
        Dictionary with at least ``title``, ``initial_message``, and
        ``question_answers`` from the Chat model.
    """
    logger.info("roadmap_curation_started", session_id=session_id)

    loop = asyncio.get_running_loop()

    try:
        # Step 1 — Acknowledge start
        await _publish_progress(
            session_id,
            status="in_progress",
            step="analysing_answers",
            detail="Analysing your answers to understand your needs…",
            progress_pct=10,
        )
        redis = get_redis()
        await redis.set(f"chat_data:{session_id}", json.dumps(chat_data), ex=3600)

        # Step 2 — Research phase
        await _publish_progress(
            session_id,
            status="in_progress",
            step="researching",
            detail="Researching the best resources for you…",
            progress_pct=30,
        )
        # Run blocking agent calls in a thread so the event loop stays free
        planner_result = await loop.run_in_executor(
            None,
            lambda: planner_agent.invoke(
                {"messages": [{"role": "user", "content": json.dumps(chat_data)}]}
            ),
        )
        planner_result_serializable = _serialize_agent_result(planner_result)
        logger.info(
            "planner_result", session_id=session_id, result=planner_result_serializable
        )
        await redis.set(
            f"planner_result:{session_id}",
            json.dumps(planner_result_serializable),
            ex=3600,
        )

        # Step 2b — Policy research (RAG) for company-policy items
        # Extract policy-related items from the planner output and run
        # the policy researcher agent in parallel with the internet researcher.
        policy_result_serializable: dict[str, Any] | None = None
        try:
            structured = planner_result_serializable.get("structured_response", {})
            # structured_response may be a list or a single dict depending
            # on the planner output format
            todo_items: list[dict[str, Any]] = []
            if isinstance(structured, list):
                todo_items = structured
            elif isinstance(structured, dict) and "items" in structured:
                todo_items = structured["items"]

            # Check if any planner item targets company_policy_search
            policy_items = [
                item
                for item in todo_items
                if isinstance(item, dict)
                and item.get("agent") == "company_policy_search"
            ]

            if policy_items:
                await _publish_progress(
                    session_id,
                    status="in_progress",
                    step="policy_research",
                    detail="Searching company policy documents…",
                    progress_pct=40,
                )
                policy_query = json.dumps(
                    {"chat_data": chat_data, "policy_items": policy_items}
                )
                policy_result = await loop.run_in_executor(
                    None,
                    lambda: policy_researcher_agent.invoke(
                        {"messages": [{"role": "user", "content": policy_query}]}
                    ),
                )
                policy_result_serializable = _serialize_agent_result(policy_result)
                logger.info(
                    "policy_research_result",
                    session_id=session_id,
                    result=policy_result_serializable,
                )
                await redis.set(
                    f"policy_result:{session_id}",
                    json.dumps(policy_result_serializable),
                    ex=3600,
                )
        except Exception as policy_exc:
            logger.warning(
                "policy_research_skipped",
                session_id=session_id,
                reason=str(policy_exc),
            )

        # Step 3 — Planning
        await _publish_progress(
            session_id,
            status="in_progress",
            step="planning",
            detail="Building your personalised learning roadmap…",
            progress_pct=60,
        )
        researcher_result = await loop.run_in_executor(
            None,
            lambda: researcher_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": json.dumps(planner_result_serializable),
                        }
                    ]
                }
            ),
        )
        researcher_result_serializable = _serialize_agent_result(researcher_result)
        logger.info(
            "researcher_result",
            session_id=session_id,
            result=researcher_result_serializable,
        )
        await redis.set(
            f"researcher_result:{session_id}",
            json.dumps(researcher_result_serializable),
            ex=3600,
        )

        with open("temp/debug_researcher.json", "w") as f:
            json.dump(researcher_result_serializable, f, indent=2)

        # Step 4 — Generating roadmap structure
        await _publish_progress(
            session_id,
            status="in_progress",
            step="generating_roadmap",
            detail="Generating the roadmap structure…",
            progress_pct=85,
        )

        roadmap_input = json.dumps(
            {
                "chat_data": chat_data,
                "researcher_output": researcher_result_serializable,
                **(
                    {"policy_research": policy_result_serializable}
                    if policy_result_serializable
                    else {}
                ),
            }
        )
        roadmap_raw = await loop.run_in_executor(
            None,
            lambda: roadmap_creator_agent.invoke(
                {"messages": [{"role": "user", "content": roadmap_input}]}
            ),
        )
        logger.info("roadmap_raw", session_id=session_id, result=roadmap_raw)

        roadmap_data = get_structured_output_parser(roadmap_raw)
        roadmap = post_process_roadmap(roadmap_data)

        logger.info("roadmap_processed", session_id=session_id, roadmap=roadmap)
        await redis.set(f"roadmap:{session_id}", json.dumps(roadmap), ex=3600)

        with open("temp/debug_roadmap.json", "w") as f:
            json.dump(roadmap, f, indent=2)

        # Step 5 — Done
        await _publish_progress(
            session_id,
            status="completed",
            step="done",
            detail="Your roadmap is ready!",
            progress_pct=100,
            roadmap=roadmap,
        )

        logger.info("roadmap_curation_completed", session_id=session_id)

    except asyncio.CancelledError:
        logger.warning("roadmap_curation_cancelled", session_id=session_id)
        await _publish_progress(
            session_id,
            status="error",
            step="cancelled",
            detail="Roadmap generation was cancelled.",
            progress_pct=0,
        )
    except Exception as exc:
        logger.error("roadmap_curation_failed", session_id=session_id, error=str(exc))
        await _publish_progress(
            session_id,
            status="error",
            step="failed",
            detail=f"Something went wrong while creating your roadmap: {exc}",
            progress_pct=0,
        )
