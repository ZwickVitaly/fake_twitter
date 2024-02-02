from .controllers import (
    api_users_router,
    api_tweets_router,
    api_like_router,
    login_router,
    users_router,
    likes_router,
    reposts_router,
)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .lifespan import basic_lifespan


static = StaticFiles(directory="fake_twttr_app/static")


app = FastAPI(lifespan=basic_lifespan)
app.include_router(api_users_router, prefix="/api")
app.include_router(api_like_router, prefix="/api")
app.include_router(api_tweets_router, prefix="/api")
app.include_router(login_router, prefix="")
app.include_router(users_router, prefix="")
app.include_router(likes_router, prefix="")
app.include_router(reposts_router, prefix="")
app.mount(path="/static", app=static)

