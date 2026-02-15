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

import json
import uuid
from typing import Any

import structlog

from ..core.redis import get_redis, roadmap_channel, roadmap_state_key

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Progress publisher helper
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Stub roadmap builder — replace internals with real agent orchestration
# ---------------------------------------------------------------------------


def _build_stub_roadmap(session_id: str, chat_data: dict[str, Any]) -> dict[str, Any]:
    """Return a placeholder roadmap structure.

    Replace this with real planner/researcher agent calls once the
    engine pipeline is wired up.
    """
    roadmap_id = str(uuid.uuid4())
    return {
        "id": roadmap_id,
        "session_id": session_id,
        "title": chat_data.get("title", "Your Tailored Learning Roadmap"),
        "objective": "Master the topics identified during onboarding",
        "description": (
            "A personalised learning path curated from your onboarding answers."
        ),
        "level": "beginner",
        "totalEstimatedDuration": "4 weeks",
        "sections": [
            {
                "id": str(uuid.uuid4()),
                "title": "Getting Started",
                "description": "Foundational concepts to kick things off.",
                "topics": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Introduction & Setup",
                        "description": "Environment setup and first steps.",
                        "status": "not_started",
                        "estimatedDuration": "1 hour",
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Core Concepts",
                        "description": "Understand the fundamental building blocks.",
                        "status": "not_started",
                        "estimatedDuration": "2 hours",
                    },
                ],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Deep Dive",
                "description": "Hands-on practice with real-world examples.",
                "topics": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Practical Exercises",
                        "description": "Apply what you have learnt so far.",
                        "status": "not_started",
                        "estimatedDuration": "3 hours",
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Advanced Patterns",
                        "description": "Go beyond the basics.",
                        "status": "not_started",
                        "estimatedDuration": "2 hours",
                    },
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


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
    import asyncio

    logger.info("roadmap_curation_started", session_id=session_id)

    try:
        # Step 1 — Acknowledge start
        await _publish_progress(
            session_id,
            status="in_progress",
            step="analysing_answers",
            detail="Analysing your answers to understand your needs…",
            progress_pct=10,
        )
        await asyncio.sleep(1.5)  # simulate work — remove when real agent is wired

        # Step 2 — Research phase
        await _publish_progress(
            session_id,
            status="in_progress",
            step="researching",
            detail="Researching the best resources for you…",
            progress_pct=30,
        )
        await asyncio.sleep(2)  # simulate work

        # Step 3 — Planning
        await _publish_progress(
            session_id,
            status="in_progress",
            step="planning",
            detail="Building your personalised learning roadmap…",
            progress_pct=60,
        )
        await asyncio.sleep(2)  # simulate work

        # Step 4 — Generating roadmap structure
        await _publish_progress(
            session_id,
            status="in_progress",
            step="generating_roadmap",
            detail="Generating the roadmap structure…",
            progress_pct=85,
        )
        await asyncio.sleep(1)  # simulate work

        # ------------------------------------------------------------------
        # TODO: Replace stub with real agent orchestration
        #   roadmap = await run_planner_and_researcher(chat_data)
        # ------------------------------------------------------------------
        roadmap = _build_stub_roadmap(session_id, chat_data)

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

    except Exception as exc:
        logger.error("roadmap_curation_failed", session_id=session_id, error=str(exc))
        await _publish_progress(
            session_id,
            status="error",
            step="failed",
            detail=f"Something went wrong while creating your roadmap: {exc}",
            progress_pct=0,
        )
