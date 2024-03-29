"""
Endpoints for creating new users via admin credentials
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fake_twttr_app.app.auth_wrappers import check_is_admin
from fake_twttr_app.app.schemas import CreatedUserSchema, AdminSchema, BadResultSchema, IntegrityErrorResponse, DefaultPositiveResult
from fake_twttr_app.db import User, async_session, Tweet, Like
from fake_twttr_app.app.config import logger_name


api_admin_router = APIRouter(
    prefix="/admin/user", tags=["admin"], include_in_schema=False
)

logger = logging.getLogger(logger_name)


@api_admin_router.post(
    "",
    responses={
        200: {"model": CreatedUserSchema},
        409: {"model": BadResultSchema}
    }
)
@check_is_admin
async def create_new_user(request: Request, admin_schema: AdminSchema):
    logger.warning("Request for new user creation")
    async with async_session() as session:
        async with session.begin():
            try:
                new_user = User(**admin_schema.new_user_data.model_dump())
                session.add(new_user)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23505":
                    logger.warning("User already exists")
                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse("User with this data (name OR api-key) already exists").to_json()
                    )
            logger.warning(f"New user {await new_user.to_safe_json()} created by admin {admin_schema.login}")
            return CreatedUserSchema(created_user_data=new_user.to_json())


@api_admin_router.delete(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        404: {"model": BadResultSchema},
    }
)
@check_is_admin
async def delete_user(request: Request, admin_schema: AdminSchema):
    logger.warning(f"Attempting user delete. User: {admin_schema.new_user_data.name} Admin: {admin_schema.login}")
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(User)
                .options(selectinload(User.user_tweet_repost))
                .options(
                    selectinload(User.tweets).options(
                        selectinload(Tweet.user_tweet_repost)
                    ).options(selectinload(Tweet.tweet_likes).options(selectinload(Like.user)))
                )
                .options(selectinload(User.followed))
                .options(selectinload(User.followers))
                .options(selectinload(User.user_likes))
                .filter_by(**admin_schema.new_user_data.model_dump())
            )
            deleted_user = query.unique().scalar_one_or_none()
            if not deleted_user:
                logger.warning(f"User {admin_schema.new_user_data.model_dump()} not found")
                return JSONResponse(
                    status_code=404,
                    content=IntegrityErrorResponse("User not found").to_json(),
                )
            logger.warning(f"User {await deleted_user.to_safe_json()} deleted by {admin_schema.login}")
            await session.delete(deleted_user)
            await session.commit()
    return {"result": True}
