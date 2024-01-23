from functools import wraps
from fastapi import Request
from fastapi.exception_handlers import HTTPException
from fake_twttr_app.db.models import User


def auth_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        api_key = request.headers.get("api-key")
        if not api_key:
            raise HTTPException(403, detail="Valid api-token required")

        user = await User.get_user_by_api_token(api_key)
        if not user:
            raise HTTPException(403, detail="User with current api-key does not exist")

        return await func(request, *args, **kwargs)

    return wrapper
