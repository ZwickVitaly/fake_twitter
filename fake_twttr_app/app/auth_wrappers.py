"""
Authentication wrappers module
"""

import logging

from functools import wraps

from fastapi import Request
from fastapi.responses import JSONResponse

from fake_twttr_app.db import Admin, User

from .config import api_key_keyword, logger_name
from .schemas import AdminSchema, UnAuthenticatedErrorResponse


logger = logging.getLogger(logger_name)


def auth_required_header(func):
    logger.debug("Checking authentication header")

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        api_key = request.headers.get(api_key_keyword)
        if not api_key:
            logger.debug("Header not found")
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse("missing valid api-key").to_json(),
            )
        logger.debug("Header found")
        user = await User.get_user_by_api_token(api_key)
        if not user:
            logger.debug("User with header not found")
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse(
                    "user with these credentials does not exist"
                ).to_json(),
            )
        logger.debug("User found")
        return await func(request, *args, **kwargs)

    logger.debug("Check complete")
    return wrapper


def check_is_admin(func):
    logger.debug("Checking is this admin")

    @wraps(func)
    async def wrapper(
        request: Request, admin_schema: AdminSchema, *args, **kwargs
    ):
        admin_data = admin_schema.model_dump(exclude={"new_user_data"})
        if not await Admin.is_admin(**admin_data):
            logger.debug("Admin credentials not found")
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse(
                    "Bad credentials"
                ).to_json(),
            )
        logger.debug("It is admin")
        return await func(request, admin_schema, *args, **kwargs)

    logger.debug("Check complete")
    return wrapper
