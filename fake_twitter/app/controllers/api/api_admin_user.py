"""
Endpoints for creating new users via admin credentials
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from fake_twitter.app.auth_wrappers import check_is_admin
from fake_twitter.app.config import logger_name
from fake_twitter.app.schemas import (
    AdminSchema,
    BadResultSchema,
    CreatedUserSchema,
    DefaultPositiveResult,
    IntegrityErrorResponse,
)
from fake_twitter.db import Like, Tweet, User, async_session

api_admin_router = APIRouter(prefix="/admin/user", include_in_schema=False)

logger = logging.getLogger(logger_name)


@api_admin_router.post(
    "", responses={200: {"model": CreatedUserSchema}, 409: {"model": BadResultSchema}}
)
@check_is_admin
async def create_new_user(request: Request, admin_schema: AdminSchema):
    """
    Endpoint to create new User in database.

    Requires admin credentials
    """
    logger.warning("Request for new user creation")
    async with async_session() as session:
        async with session.begin():
            try:
                new_user = User(**admin_schema.user_data.model_dump())
                session.add(new_user)
                await session.commit()
            except IntegrityError as e:
                if e.orig.__getattribute__("pgcode") == "23505":
                    logger.warning("User already exists")
                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse(
                            "User with this data (name OR api-key) already exists"
                        ).to_json(),
                    )
                else:
                    raise
            logger.warning(f"New user {await new_user.to_safe_json()} created")
            return CreatedUserSchema(created_user_data=new_user.to_json())  # type: ignore[arg-type]


@api_admin_router.delete(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        404: {"model": BadResultSchema},
    },
)
@check_is_admin
async def delete_user(request: Request, admin_schema: AdminSchema):
    """
    Endpoint to delete User from database.

    Both username and api-key are unique values for database
    Consider using highly random string like uuid4 or uuid7 for api-key

    Requires admin credentials.
    """
    logger.warning(f"Attempting user delete. User: {admin_schema.user_data.name}")
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(User)
                .options(selectinload(User.user_tweet_repost))
                .options(
                    selectinload(User.tweets)
                    .options(selectinload(Tweet.user_tweet_repost))
                    .options(
                        selectinload(Tweet.tweet_likes).options(selectinload(Like.user))
                    )
                )
                .options(selectinload(User.followed))
                .options(selectinload(User.followers))
                .options(selectinload(User.user_likes))
                .filter_by(**admin_schema.user_data.model_dump())
            )
            deleted_user = query.unique().scalar_one_or_none()
            if not deleted_user:
                logger.warning(f"User {admin_schema.user_data.model_dump()} not found")
                return JSONResponse(
                    status_code=404,
                    content=IntegrityErrorResponse("User not found").to_json(),
                )
            logger.warning(f"User {await deleted_user.to_safe_json()} deleted")
            await session.delete(deleted_user)
            await session.commit()
    return DefaultPositiveResult()
