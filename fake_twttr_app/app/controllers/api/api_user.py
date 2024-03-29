"""
Endpoints for getting user's info
"""

import logging
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Result, select
from sqlalchemy.orm import selectinload

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.config import api_key_keyword, logger_name
from fake_twttr_app.app.schemas import ProfileResultSchema, BadResultSchema, ValidationErrorResultSchema
from fake_twttr_app.db import Tweet, User, Like
from fake_twttr_app.db.base import async_session


api_users_router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(logger_name)


@api_users_router.get(
    "/{user_id:int}",
    responses={
        200: {"model": ProfileResultSchema},
        404: {"model": BadResultSchema},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@api_users_router.get(
    "/me",
    responses={
        200: {"model": ProfileResultSchema},
        404: {"model": BadResultSchema},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def get_my_info_handler(request: Request, user_id: Optional[int] = None):
    if user_id:
        logger.debug(f"Requesting User: User.id={user_id}")
        key = (User.id == user_id)
    else:
        logger.debug("Self info request")
        key = User.api_key.ilike(request.headers.get(api_key_keyword))
    async with async_session() as session:
        async with session.begin():
            query: Result[tuple[User]] = await session.execute(
                select(User)
                .options(selectinload(User.user_tweet_repost))
                .options(
                    selectinload(User.tweets).options(
                        selectinload(Tweet.user_tweet_repost)
                    ).options(selectinload(Tweet.tweet_likes).options(selectinload(Like.user)))
                )
                .options(selectinload(User.followed))
                .options(selectinload(User.followers))
                .filter(key)
            )
            user: User | None = query.unique().scalar_one_or_none()
            if not user:
                logger.debug(f"User.id={user_id} not found")
                return JSONResponse(
                    status_code=404,
                    content={
                        "result": False,
                        "error_type": "Not found",
                        "error_msg": "User is not found",
                    },
                )

            my_reposts = [await repost.to_safe_json() for repost in user.user_tweet_repost]
            tweets = [await tweet.to_safe_json() for tweet in user.tweets]
            my_followed = [await user.to_safe_json() for user in user.followed]
            my_followers = [await user.to_safe_json() for user in user.followers]

            result = await user.to_safe_json()

            tweets.extend(my_reposts)
            tweets.sort(key=lambda x: x.get("created_at"), reverse=True)
            result.update(
                {
                    "tweets": tweets,
                    "following": my_followed,
                    "followers": my_followers,
                }
            )
            logger.debug("Requesting User info: success")
            return {"user": result}
