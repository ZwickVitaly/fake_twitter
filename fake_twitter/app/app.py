"""
Main app module
"""

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import media_path, static_request_path
from .controllers import (
    api_admin_router,
    api_follows_router,
    api_likes_router,
    api_media_router,
    api_tweets_router,
    api_users_router,
)
from .lifespan import basic_lifespan
from .schemas import BadResultSchema

app = FastAPI(lifespan=basic_lifespan)

static = StaticFiles(directory=media_path, check_dir=False)

logger = logging.getLogger("uvicorn")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Redefined 422 response.
    """
    logger.debug("Unprocessable entity")
    return JSONResponse(
        status_code=422,
        content=BadResultSchema(
            error_type="Validation error", error_msg=exc.errors()
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def bad_request_exception_handler(request: Request, exc: HTTPException):
    """
    Redefined 400 response
    """
    logger.debug("Bad request")
    return JSONResponse(
        status_code=400,
        content=BadResultSchema(
            error_type="Bad request", error_msg=exc.detail
        ).model_dump(),
    )


logger.debug("Including routers")

# Plugging in routers

app.include_router(api_users_router, prefix="/api")
app.include_router(api_likes_router, prefix="/api")
app.include_router(api_tweets_router, prefix="/api")

# app.include_router(api_reposts_router, prefix="/api")
app.include_router(api_follows_router, prefix="/api")
app.include_router(api_admin_router, prefix="/api")
app.include_router(api_media_router, prefix="/api")

# Creating static directory if not exists

os.makedirs(media_path, exist_ok=True)

logger.debug("Mounting static folder")

# Mounting static directory
app.mount(path=static_request_path, app=static)
