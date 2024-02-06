from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.keywords import api_key_keyword
from fake_twttr_app.app.schemas import (
    BadResultSchema,
    BadUuidResponse,
    DefaultResult,
    IntegrityErrorResponse,
    ValidationErrorResultSchema,
)
from fake_twttr_app.db import Repost, User
from fake_twttr_app.db.base import async_session

api_reposts_router = APIRouter(
    prefix="/tweets/{tweet_uuid:str}/repost", tags=["reposts"]
)


@api_reposts_router.post(
    "",
    responses={
        200: {"model": DefaultResult},
        403: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def post_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).uuid
            try:
                new_repost = Repost(user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid))
                session.add(new_repost)
                await session.commit()
            except ValueError:
                return JSONResponse(
                    status_code=422, content=BadUuidResponse().to_json()
                )
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    return JSONResponse(
                        status_code=404,
                        content=IntegrityErrorResponse("Tweet not found").to_json(),
                    )
                elif e.orig.pgcode == "23505":
                    return JSONResponse(
                        status_code=409,
                        content=IntegrityErrorResponse(
                            "You already reposted this tweet"
                        ).to_json(),
                    )
                else:
                    raise
    return DefaultResult()


@api_reposts_router.delete(
    "",
    responses={
        200: {"model": DefaultResult},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def delete_like_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).uuid
            try:
                like_q = delete(Repost).filter_by(
                    user_uuid=user_uuid, tweet_uuid=UUID(tweet_uuid)
                )
                await session.execute(like_q)
            except ValueError:
                return JSONResponse(
                    status_code=422, content=BadUuidResponse().to_json()
                )
    return DefaultResult()
