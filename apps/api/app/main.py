"""FastAPI application factory and error-handler wiring."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.errors import ApiError
from app.routers import (
    health,
    languages,
    lexicon,
    models,
    pronunciation,
    synthesis,
    synthesis_ws,
    system,
    text,
    voices,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="VaaniLab API", version=settings.api_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "request validation failed",
                    "details": {"errors": jsonable_encoder(exc.errors())},
                }
            },
        )

    for router in (
        health.router,
        system.router,
        models.router,
        voices.router,
        languages.router,
        text.router,
        pronunciation.router,
        lexicon.router,
        synthesis.router,
        synthesis_ws.router,
    ):
        app.include_router(router)

    return app


app = create_app()
