from app.api.v1 import router as api_v1_router
from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title="Proactive Onboarding Engine API", version="0.1.0")


app.include_router(api_v1_router, prefix="/v1")
