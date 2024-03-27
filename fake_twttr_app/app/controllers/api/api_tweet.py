from os import path as os_path
from os import remove as os_remove

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import String, select, update

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.folders import media_path
from fake_twttr_app.app.keywords import api_key_keyword
from fake_twttr_app.app.schemas import (
    BadResultSchema,
    DefaultPositiveResult,
    NewTweetSchema,
    NotFoundErrorResponse,
    ResultFeedSchema,
    ResultTweetCreationSchema,
    ResultTweetSchema,
    FeedOutSchema,
    UnAuthorizedErrorResponse,
    ValidationErrorResultSchema,
)
from fake_twttr_app.db import Follow, Image, Tweet, User
from fake_twttr_app.db.base import async_session

api_tweets_router = APIRouter(prefix="/tweets", tags=["tweets"])


@api_tweets_router.get(
    "",
    responses={
        200: {"model": ResultFeedSchema},
        401: {"model": BadResultSchema},
    },
)
@auth_required_header
async def get_feed_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            q = await session.execute(
                select(Tweet)
                .order_by(Tweet.views.desc())
                .order_by(Tweet.created_at.desc())
            )
            tweets = q.scalars().unique().all()
            tweet_list = [await t.to_safe_json() for t in tweets]
            tweet_list.sort(key=lambda x: x["likes"], reverse=True)
            return FeedOutSchema(tweets=tweet_list)


@api_tweets_router.get(
    "/feed",
    responses={
        200: {"model": ResultFeedSchema},
        401: {"model": BadResultSchema},
    },
)
@auth_required_header
async def get_personal_feed_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            user = await User.get_user_by_api_token(
                request.headers.get(api_key_keyword)
            )
            q = await session.execute(
                select(Tweet)
                .join(User)
                .join(Follow, User.id == Follow.followed_user)
                .filter_by(follower_user=user.id)
                .order_by(Tweet.views.desc())
                .order_by(Tweet.created_at.desc())
            )
            tweets = q.scalars().unique().all()
            tweet_list = [await t.to_safe_json() for t in tweets]
            tweet_list.sort(key=lambda x: x["likes"], reverse=True)
            return {"tweets": tweet_list}


@api_tweets_router.get(
    "/{tweet_id:int}",
    responses={
        200: {"model": ResultTweetSchema},
        401: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def get_tweet_handler(request: Request, tweet_id: int):
    async with async_session() as session:
        async with session.begin():
            tweets_filter = Tweet.id.ilike(tweet_id)
            await session.execute(
                update(Tweet).where(tweets_filter).values(views=Tweet.views + 1)
            )
            tweet_q = await session.execute(
                select(Tweet).join(User).filter(tweets_filter)
            )
            tweet = tweet_q.unique().scalar_one_or_none()
            if not tweet:
                return JSONResponse(
                    status_code=404,
                    content=NotFoundErrorResponse("Tweet not found").to_json(),
                )
            return {"tweet": await tweet.to_safe_json()}


@api_tweets_router.post(
    "",
    responses={
        200: {"model": ResultTweetCreationSchema},
        401: {"model": BadResultSchema},
        422: {"model": ValidationErrorResultSchema},
    },
)
@auth_required_header
async def post_tweet_handler(request: Request, new_tweet_data: NewTweetSchema):
    async with async_session() as session:
        async with session.begin():
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            new_tweet = Tweet(content=new_tweet_data.tweet_data, user_id=user_id)
            session.add(new_tweet)
            if new_tweet_data.tweet_media:
                for image_id in new_tweet_data.tweet_media:
                    image = await session.execute(select(Image).filter_by(id=image_id))
                    if not image.scalar_one_or_none():
                        await session.close()
                        return JSONResponse(
                            status_code=422,
                            content=NotFoundErrorResponse(
                                f"Image id={image_id} is not downloaded yet"
                            ).to_json(),
                        )
                    await session.execute(
                        update(Image)
                        .where(Image.id == image_id)
                        .values(tweet_id=new_tweet.id)
                    )
            await session.commit()

    return ResultTweetCreationSchema(tweet_id=new_tweet.id)


@api_tweets_router.delete(
    "/{tweet_id:int}",
    responses={
        200: {"model": DefaultPositiveResult},
        401: {"model": BadResultSchema},
        403: {"model": BadResultSchema},
        404: {"model": BadResultSchema},
    },
)
@auth_required_header
async def delete_tweet_handler(request: Request, tweet_id: int):
    async with async_session() as session:
        async with session.begin():
            tweets_filter = Tweet.id.ilike(tweet_id)
            user_id = (
                await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            ).id
            deleted_tweet = (
                (await session.execute(select(Tweet).filter(tweets_filter)))
                .unique()
                .scalar_one_or_none()
            )
            if not deleted_tweet:
                return JSONResponse(
                    status_code=404,
                    content=NotFoundErrorResponse("Tweet is not found").to_json(),
                )
            elif deleted_tweet.tweet_author.id != user_id:
                return JSONResponse(
                    status_code=403,
                    content=UnAuthorizedErrorResponse(
                        "This is not your tweet"
                    ).to_json(),
                )
            for image in deleted_tweet.images_objects:
                removed_image_path = os_path.join(
                    media_path, f"{image.id}{image.file_extension}"
                )
                os_remove(removed_image_path)
            await session.delete(deleted_tweet)
            await session.commit()
    return DefaultPositiveResult()
