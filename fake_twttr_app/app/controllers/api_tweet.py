from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select, String, update

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.db.base import async_session
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User, Tweet, Image, Follow
from fake_twttr_app.app.schemas import NewTweetSchema

api_tweets_router = APIRouter(
    prefix="/tweets",
    tags=["tweets"]
)


@api_tweets_router.get("/feed")
@auth_required_header
async def get_feed_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            tweets_filter = User.api_key.not_like(request.headers.get(api_key_keyword))
            q = await session.execute(select(Tweet).join(User).filter(tweets_filter).order_by(Tweet.views.desc()).order_by(Tweet.created_at.desc()))
            tweets = q.scalars().unique().all()
            tweet_list = [t.to_safe_json() for t in tweets]
            tweet_list.sort(key=lambda x: x["likes"], reverse=True)
            return {"tweets": tweet_list}


@api_tweets_router.get("/feed/personal")
@auth_required_header
async def get_personal_feed_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            user = await User.get_user_by_api_token(request.headers.get(api_key_keyword))
            q = await session.execute(select(Tweet).join(User).join(Follow, User.uuid == Follow.followed_user).filter_by(follower_user=user.uuid).order_by(Tweet.views.desc()).order_by(Tweet.created_at.desc()))
            tweets = q.scalars().unique().all()
            tweet_list = [t.to_safe_json() for t in tweets]
            tweet_list.sort(key=lambda x: x["likes"], reverse=True)
            return {"tweets": tweet_list}


@api_tweets_router.get("/{tweet_uuid:str}")
@auth_required_header
async def get_tweet_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            tweets_filter = Tweet.uuid.cast(String).ilike(tweet_uuid)
            await session.execute(update(Tweet).where(tweets_filter).values(views=Tweet.views + 1))
            tweet_q = await session.execute(select(Tweet).join(User).filter(tweets_filter))
            tweet = tweet_q.unique().scalar_one_or_none()
            if not tweet:
                raise HTTPException(404, "Tweet not found")
            return tweet.to_safe_json()


@api_tweets_router.post("")
@auth_required_header
async def post_tweet_handler(request: Request, new_tweet_data: NewTweetSchema):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.headers.get(api_key_keyword))).uuid
            new_tweet = Tweet(content=new_tweet_data.tweet_data, user_uuid=user_uuid)
            session.add(new_tweet)
            await session.commit()

        if new_tweet_data.tweet_media:
            async with session.begin():
                new_image = Image(source=new_tweet_data.tweet_media, tweet_uuid=new_tweet.uuid)
                session.add(new_image)
                await session.commit()

    return {"result": True, "tweet_id": new_tweet.uuid}


@api_tweets_router.delete("/{tweet_uuid:str}")
@auth_required_header
async def delete_tweet_handler(request: Request, tweet_uuid: str):
    async with async_session() as session:
        async with session.begin():
            tweets_filter = Tweet.uuid.cast(String).ilike(tweet_uuid)
            user_uuid = (await User.get_user_by_api_token(request.headers.get(api_key_keyword))).uuid
            deleted_tweet = (await session.execute(select(Tweet).filter(tweets_filter))).unique().scalar_one_or_none()
            if not deleted_tweet:
                raise HTTPException(404, "Tweet is not found")
            elif deleted_tweet.tweet_author.uuid != user_uuid:
                raise HTTPException(403, "This is not your tweet")
            await session.delete(deleted_tweet)
    return {"result": True}
