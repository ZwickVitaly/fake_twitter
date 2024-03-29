"""
Main app module
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from .controllers import (
    api_admin_router,
    api_follows_router,
    api_likes_router,
    api_media_router,
    api_reposts_router,
    api_tweets_router,
    api_users_router,
)
from .config import static, static_request_path
from .lifespan import basic_lifespan
from .schemas import BadResultSchema, ValidationErrorResultSchema


app = FastAPI(lifespan=basic_lifespan)

logger = logging.getLogger("uvicorn")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Redefined 422 response.
    """
    logger.debug("Unprocessable entity")
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResultSchema(
            error_type="ValidationError", error_msg=exc.errors()
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
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
app.include_router(api_users_router, prefix="/api")
app.include_router(api_likes_router, prefix="/api")
app.include_router(api_tweets_router, prefix="/api")
app.include_router(api_reposts_router, prefix="/api")
app.include_router(api_follows_router, prefix="/api")
app.include_router(api_admin_router, prefix="/api")
app.include_router(api_media_router, prefix="/api")
logger.debug("Mounting static folder")
app.mount(path=static_request_path, app=static)
