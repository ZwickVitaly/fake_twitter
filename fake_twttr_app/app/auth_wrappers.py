from functools import wraps

from fastapi import Request
from fastapi.responses import JSONResponse

from fake_twttr_app.db import Admin, User

from .keywords import api_key_keyword
from .schemas import AdminSchema, UnAuthenticatedErrorResponse


def auth_required_header(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        api_key = request.headers.get(api_key_keyword)
        if not api_key:
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse("missing valid api-key").to_json(),
            )

        user = await User.get_user_by_api_token(api_key)
        if not user:
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse(
                    "user with this api-key does not exist"
                ).to_json(),
            )

        return await func(request, *args, **kwargs)

    return wrapper


def check_is_admin(func):
    @wraps(func)
    async def wrapper(
        request: Request, admin_schema: AdminSchema, *args, **kwargs
    ):
        admin_data = admin_schema.model_dump(exclude={"new_user_data"})
        if not await Admin.is_admin(**admin_data):
            return JSONResponse(
                status_code=401,
                content=UnAuthenticatedErrorResponse(
                    "Bad credentials"
                ).to_json(),
            )

        return await func(request, admin_schema, *args, **kwargs)

    return wrapper
