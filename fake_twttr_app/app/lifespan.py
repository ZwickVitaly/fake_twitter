import time
from contextlib import asynccontextmanager
from time import sleep

from fake_twttr_app.db.base import engine, async_session
from fake_twttr_app.db.models import (
    Base,
    User,
    Tweet,
    Image,
    Like,
    Repost,
    Follows,
)


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        new_user = User(display_name="Loki", api_key="123")
        new_user_2 = User(display_name="Floki", api_key="321")
    async with async_session() as session:
        session.add(new_user)
        session.add(new_user_2)
        await session.commit()
        floki_loki = Follows(followed_user=new_user.uuid, follower_user=new_user_2.uuid)
        loki_floki = Follows(followed_user=new_user_2.uuid, follower_user=new_user.uuid)
        session.add(floki_loki)
        session.add(loki_floki)
        new_tweet_loki = Tweet(content="ROFL MOFL SHITHEADS", user_uuid=new_user.uuid)
        new_tweet_2 = Tweet(content="STILL MOFL ROFL", user_uuid=new_user.uuid)
        new_tweet_floki = Tweet(content="I AM NOT AGREE WITH U, DCK HD", user_uuid=new_user_2.uuid)
        session.add(new_tweet_loki)
        session.add(new_tweet_2)
        session.add(new_tweet_floki)
        await session.commit()
        floki_likes_loki = Like(tweet_uuid=new_tweet_loki.uuid, user_uuid=new_user_2.uuid)
        session.add(floki_likes_loki)
        floki_reposts_loki = Repost(tweet_uuid=new_tweet_loki.uuid, user_uuid=new_user_2.uuid)
        session.add(floki_reposts_loki)
        await session.commit()
    yield
    async with async_session() as session:
        await session.delete(new_tweet_loki)
        await session.delete(new_tweet_2)
        await session.delete(new_tweet_floki)
        await session.delete(new_user)
        await session.delete(new_user_2)
        await session.commit()
    await engine.dispose()
