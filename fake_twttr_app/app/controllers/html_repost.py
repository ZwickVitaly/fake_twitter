from uuid import UUID

import asyncpg
from fastapi import APIRouter, Request, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

from fake_twttr_app.app.auth_wrappers import auth_required_cookie
from fake_twttr_app.db.base import async_session
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User, Repost

reposts_router = APIRouter(
    prefix="/tweets/{tweet_uuid:str}/repost"
)


@reposts_router.post("")
@auth_required_cookie
async def post_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
            new_repost = Repost(user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid))
            try:
                session.add(new_repost)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    raise HTTPException(404, "Tweet does not exist")
                elif e.orig.pgcode == "23505":
                    raise HTTPException(403, "You have already reposted this tweet")
                else:
                    raise
    return Response(status_code=201)


@reposts_router.delete("")
@auth_required_cookie
async def delete_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
            like_q = delete(Repost).filter_by(user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid))
            await session.execute(like_q)
    return Response(status_code=201)
