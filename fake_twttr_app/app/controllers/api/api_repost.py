"""
Endpoints for Repost CRUD
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.config import api_key_keyword, logger_name
from fake_twttr_app.app.schemas import (
    BadResultSchema,
    DefaultPositiveResult,
    IntegrityErrorResponse,
    ValidationErrorResultSchema,
)
from fake_twttr_app.db import Repost, User
from fake_twttr_app.db.base import async_session

api_reposts_router = APIRouter(
    prefix="/tweets/{tweet_id:int}/repost", tags=["reposts"]
)
logger = logging.getLogger("uvicorn")


@api_reposts_router.post(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        403: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def post_like_handler(request: Request, tweet_id: int):
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            logger.debug(f"Attempting Repost: User.id={user_id} Tweet.id={tweet_id}")
            try:
                new_repost = Repost(user_id=user_id, tweet_id=tweet_id)
                session.add(new_repost)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    logger.debug(f"Repost: User.id={user_id} Tweet.id={tweet_id} - fail - tweet not found")
                    return JSONResponse(
                        status_code=404,
                        content=IntegrityErrorResponse("Tweet not found").to_json(),
                    )
                elif e.orig.pgcode == "23505":
                    logger.debug(f"Repost: User.id={user_id} Tweet.id={tweet_id} - fail - already reposted")

                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse(
                            "You already reposted this tweet"
                        ).to_json(),
                    )
                else:
                    raise
    logger.debug(f"Repost: User.id={user_id} Tweet.id={tweet_id} - success")
    return DefaultPositiveResult()


@api_reposts_router.delete(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def delete_like_handler(request: Request, tweet_id: int):
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            like_q = delete(Repost).filter_by(
                user_id=user_id, tweet_id=tweet_id
            )
            await session.execute(like_q)
    logger.debug(f"delete Repost: User.id={user_id} Tweet.id={tweet_id}")
    return DefaultPositiveResult()
