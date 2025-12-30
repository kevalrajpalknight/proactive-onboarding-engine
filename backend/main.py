"""Backend entry point for the Proactive Onboarding Engine.

Run with:
    uv run uvicorn app.main:app --reload
"""

from app.main import app  # noqa: F401
