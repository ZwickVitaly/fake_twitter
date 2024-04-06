"""
Endpoints for Like CRUD
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from fake_twitter.app.auth_wrappers import auth_required_header
from fake_twitter.app.config import api_key_keyword, logger_name
from fake_twitter.app.schemas import (
    BadResultSchema,
    DefaultPositiveResult,
    IntegrityErrorResponse,
)
from fake_twitter.db import Like, User, async_session

api_likes_router = APIRouter(prefix="/tweets/{tweet_id:int}/likes", tags=["likes"])

logger = logging.getLogger(logger_name)


@api_likes_router.post(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
    },
)
@auth_required_header
async def post_like_handler(request: Request, tweet_id: int):
    """
    Endpoint to post like tweet by id.

    User is recognized by api-key header value

    User can like tweet only once

    <h3>Requires api-key header with valid api key</h3>
    """
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            logger.debug(f"Attempting Like: User.id={user_id} Tweet.id={tweet_id}")
            try:
                new_like = Like(user_id=user_id, tweet_id=tweet_id)
                session.add(new_like)
                await session.commit()
            except IntegrityError as e:
                pgcode = e.orig.__getattribute__("pgcode")
                if pgcode == "23503":
                    logger.debug(
                        f"Like: User.id={user_id} Tweet.id={tweet_id} fail - tweet does not exist"
                    )
                    return JSONResponse(
                        status_code=404,
                        content=IntegrityErrorResponse("Tweet not found").to_json(),
                    )
                elif pgcode == "23505":
                    logger.debug(
                        f"Like: User.id={user_id} Tweet.id={tweet_id} fail - like already exists"
                    )
                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse(
                            "You already liked this tweet"
                        ).to_json(),
                    )
                else:
                    raise
    logger.debug(f"Like: User.id={user_id} Tweet.id={tweet_id} success")
    return DefaultPositiveResult()


@api_likes_router.delete(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
    },
)
@auth_required_header
async def delete_like_handler(request: Request, tweet_id: int):
    """
    Endpoint to delete tweet like by tweet id.

    User is recognized by api-key header value

    User can delete only his own like

    <h3>Requires api-key header with valid api key</h3>
    """
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            like_q = delete(Like).filter_by(user_id=user_id, tweet_id=tweet_id)
            logger.debug(f"delete Like: User.id={user_id} Tweet.id={tweet_id}")
            await session.execute(like_q)

    return DefaultPositiveResult()
