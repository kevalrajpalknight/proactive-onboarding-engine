import json

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger()


def make_serializable(obj):
    """
    Convert non-serializable objects to serializable forms.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    if isinstance(obj, Exception):
        return str(obj)
    return obj


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(
            "Unhandled StarletteHTTPException", path=request.url.path, detail=str(exc)
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail or "Internal Server Error",
                "status_code": exc.status_code,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.error("Validation Error", path=request.url.path, errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "detail": make_serializable(exc.errors()),
                "body": make_serializable(exc.body),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled Exception", path=request.url.path, detail=str(exc))
        return JSONResponse(
            status_code=exc.status_code if isinstance(exc, HTTPException) else 500,
            content={
                "detail": (
                    exc.detail
                    if isinstance(exc, HTTPException)
                    else "Internal Server Error"
                ),
                "status_code": (
                    exc.status_code if isinstance(exc, HTTPException) else 500
                ),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(HTTPException)
    async def general_exception_handler(request: Request, exc: HTTPException):
        logger.error("Unhandled HTTPException ", path=request.url.path, detail=str(exc))
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
            },
        )
