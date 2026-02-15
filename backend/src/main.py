# Import all necessary modules to register models and routers
# This ensures that when the app starts, all models and routes are included properly
from contextlib import asynccontextmanager

import src.models  # noqa: F401
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.chat import routers as chat_router
from src.chat import websocket as chat_ws
from src.core.config import settings
from src.core.exceptions import setup_exception_handlers
from src.core.redis import close_redis
from src.users import routers as user_router

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        (
            structlog.processors.JSONRenderer()
            if settings.log_format == "json"
            else structlog.dev.ConsoleRenderer()
        ),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup / shutdown hooks."""
    yield
    # Shutdown: close Redis pool
    await close_redis()


app = FastAPI(
    title="Proactive Onboarding Engine API",
    version="0.1.0",
    description="API for Proactive Onboarding Engine",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup exception handlers
setup_exception_handlers(app)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(user_router.router)
app.include_router(chat_router.router)

# Include WebSocket router
app.include_router(chat_ws.router)
