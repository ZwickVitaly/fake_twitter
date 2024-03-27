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
from .lifespan import basic_lifespan
from .schemas import BadResultSchema, ValidationErrorResultSchema


app = FastAPI(lifespan=basic_lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResultSchema(
            error_type="ValidationError", error_msg=exc.errors()
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=400,
        content=BadResultSchema(
            error_type="Bad request", error_msg=exc.detail
        ).model_dump(),
    )


app.include_router(api_users_router, prefix="/api")
app.include_router(api_likes_router, prefix="/api")
app.include_router(api_tweets_router, prefix="/api")
app.include_router(api_reposts_router, prefix="/api")
app.include_router(api_follows_router, prefix="/api")
app.include_router(api_admin_router, prefix="/api")
app.include_router(api_media_router, prefix="/api")
