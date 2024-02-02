from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

from fake_twttr_app.app.auth_wrappers import auth_required_cookie
from fake_twttr_app.db.base import async_session
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User, Like

likes_router = APIRouter(
    prefix="/tweets/{tweet_uuid:str}/like"
)


@likes_router.post("")
@auth_required_cookie
async def post_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
            new_like = Like(user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid))
            try:
                session.add(new_like)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    raise HTTPException(404, "Tweet does not exist")
                elif e.orig.pgcode == "23505":
                    raise HTTPException(403, "You have already liked this tweet")
                else:
                    raise
    return Response(status_code=201)


@likes_router.delete("")
@auth_required_cookie
async def delete_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
            like_q = delete(Like).filter_by(user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid))
            await session.execute(like_q)
    return Response(status_code=201)
