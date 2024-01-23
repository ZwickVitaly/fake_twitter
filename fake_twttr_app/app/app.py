from fastapi import FastAPI, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fake_twttr_app.db.base import async_session
from fake_twttr_app.db.models import (
    User,
    Tweet,
    Image,
    Like,
    Repost,
    Follows
)

from .lifespan import basic_lifespan
from .auth_wrappers import auth_required


app = FastAPI(lifespan=basic_lifespan)


@app.get("/api/me")
@auth_required
async def get_my_info_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            usrs = await session.execute(
                select(User)
                .options(selectinload(User.user_tweet_repost))
                .options(selectinload(User.tweets).options(selectinload(Tweet.user_tweet_repost)))
                .options(selectinload(User.followed))
                .filter_by(api_key=request.headers.get("api-key"))
            )
            user = usrs.unique().scalar_one()
            reposts = [tweet.reposted_tweet.to_safe_json(user.uuid) for tweet in user.user_tweet_repost]
            tweets = [tweet.to_safe_json(user.uuid) for tweet in user.tweets]
            tweets.extend(reposts)
            tweets.sort(key=lambda x: "created_at")
            return {"name": user.display_name, "tweets": tweets}


@app.get("/api/tweets")
@auth_required
async def get_tweets_handler(request: Request):
    async with async_session() as session:
        async with session.begin():
            q = await session.execute(
                select(Tweet)
            )
            tweet = q.scalars().all()
            tweet_list = []
            for u in tweet:
                tweet_obj = u.to_safe_json()
                tweet_list.append(tweet_obj)
            return {"tweets": tweet_list}
