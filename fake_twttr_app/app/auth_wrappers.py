from functools import wraps

from fastapi import Request
from fastapi.exception_handlers import HTTPException

from fake_twttr_app.db import User
from .headers import api_key_keyword


def auth_required_header(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        api_key = request.headers.get(api_key_keyword)
        if not api_key:
            raise HTTPException(401, detail="Valid api-token required")

        user = await User.get_user_by_api_token(api_key)
        if not user:
            raise HTTPException(401, detail="User with current api-key does not exist")

        return await func(request, *args, **kwargs)

    return wrapper


def auth_required_cookie(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        api_key = request.cookies.get(api_key_keyword)
        if not api_key:
            raise HTTPException(401, detail="Valid api-token required")

        user = await User.get_user_by_api_token(api_key)
        if not user:
            raise HTTPException(401, detail="User with current api-key does not exist")

        return await func(request, *args, **kwargs)

    return wrapper
