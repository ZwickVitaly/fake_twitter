from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User


login_router = APIRouter(
    prefix="/login",
    tags=["login"]
)


templates = Jinja2Templates(directory="fake_twttr_app/static/templates")


@login_router.get("")
async def login_get_handler(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@login_router.post("")
async def login(request: Request, username: Annotated[str, Form()]):
    user = await User.get_user_by_name(username)
    if not user:
        redirect_url = request.url
        return RedirectResponse(redirect_url, status_code=303)
    response = RedirectResponse("/users/me", status_code=303)
    response.set_cookie(key=api_key_keyword, value=user.api_key)
    response.set_cookie(key="my_uuid", value=user.uuid)
    return response
