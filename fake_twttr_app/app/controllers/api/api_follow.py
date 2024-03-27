from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.keywords import api_key_keyword
from fake_twttr_app.app.schemas import (
    BadResultSchema,
    DefaultPositiveResult,
    IntegrityErrorResponse,
    ValidationErrorResultSchema,
)
from fake_twttr_app.db import Follow, User
from fake_twttr_app.db.base import async_session

api_follows_router = APIRouter(
    prefix="/users/{followed_id:int}/follow", tags=["follows"]
)


@api_follows_router.post(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
        403: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def post_follow_handler(request: Request, followed_id: int):
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            if user_id == followed_id:
                return JSONResponse(
                    status_code=409,
                    content=IntegrityErrorResponse(
                        "You can't follow yourself"
                    ).to_json(),
                )
            try:
                new_follow = Follow(
                    follower_user=user_id, followed_user=followed_id
                )
                session.add(new_follow)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    return JSONResponse(
                        status_code=404,
                        content=IntegrityErrorResponse("User not found").to_json(),
                    )
                elif e.orig.pgcode == "23505":
                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse(
                            "You are already following this user"
                        ).to_json(),
                    )

    return DefaultPositiveResult()


@api_follows_router.delete(
    "",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def delete_follow_handler(request: Request, followed_id: int):
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            like_q = delete(Follow).filter_by(
                follower_user=user_id, followed_user=followed_id
            )
            await session.execute(like_q)
            await session.commit()

    return DefaultPositiveResult()
