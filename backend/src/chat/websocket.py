"""WebSocket endpoint for streaming roadmap generation progress.

The client connects to  /ws/roadmap/{session_id}?token=<jwt>
and receives JSON messages with progress updates published via Redis pub/sub.

On connect the server first sends back any *cached* progress state so that a
page-refresh reconnects seamlessly.
"""

import json

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from ..auth.jwt import verify_access_token
from ..core.redis import get_redis, roadmap_channel, roadmap_state_key

logger = structlog.get_logger()

router = APIRouter()


async def _authenticate_ws(token: str | None) -> dict | None:
    """Validate a JWT token and return the payload or None."""
    if not token:
        return None
    try:
        payload = verify_access_token(token)
        return payload
    except Exception:
        return None


@router.websocket("/ws/roadmap/{session_id}")
async def roadmap_progress_ws(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(default=""),
):
    """Stream roadmap curation progress to the connected client.

    Flow
    ----
    1. Authenticate via the ``token`` query param.
    2. Send any cached progress so a refresh picks up where we left off.
    3. Subscribe to the Redis pub/sub channel and forward every message.
    """

    # -- Authenticate -------------------------------------------------
    payload = await _authenticate_ws(token)
    if payload is None:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()

    redis = get_redis()
    pubsub = None

    pubsub_key = roadmap_channel(session_id)
    try:
        # Send cached state (reconnection support)
        cached_raw = await redis.get(roadmap_state_key(session_id))
        if cached_raw:
            cached = (
                json.loads(cached_raw) if isinstance(cached_raw, str) else cached_raw
            )
            await websocket.send_json(cached)

        # Subscribe to real-time channel
        pubsub = redis.pubsub()
        await pubsub.subscribe(pubsub_key)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = message["data"]
            if isinstance(data, bytes):
                data = data.decode()

            try:
                payload_data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                payload_data = {"message": data}

            await websocket.send_json(payload_data)

            # If the engine signals completion, close gracefully
            if payload_data.get("status") == "completed":
                await pubsub.unsubscribe(pubsub_key)
                break

    except WebSocketDisconnect:
        logger.info(
            "ws_client_disconnected",
            session_id=session_id,
        )
    except Exception as exc:
        logger.error(
            "ws_error",
            session_id=session_id,
            error=str(exc),
        )
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
    finally:
        if pubsub is not None:
            try:
                await pubsub.unsubscribe(pubsub_key)
                await pubsub.aclose()
            except Exception:
                pass
