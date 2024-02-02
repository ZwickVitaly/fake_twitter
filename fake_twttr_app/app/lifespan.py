import time
from contextlib import asynccontextmanager


from sqlalchemy import select

from fake_twttr_app.db import Base, User, Tweet, Like, Repost, Follow, Image, engine, async_session


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        new_user = User(name="Loki", api_key="132")
        new_user_2 = User(name="Foki", api_key="321")
        new_user_3 = User(name="Choki", api_key="123")
    async with async_session() as session:
        q = await session.execute(
            select(User).filter_by(name="me")
        )
        check = q.unique().scalars().first()
        if not check:
            session.add(new_user)
        session.add(new_user_2)
        session.add(new_user_3)
        await session.commit()
        loki_floki = Follow(followed_user=new_user_2.uuid, follower_user=new_user.uuid)
        chmoki_floki = Follow(
            followed_user=new_user_2.uuid, follower_user=new_user_3.uuid
        )

        session.add(loki_floki)
        session.add(chmoki_floki)
        new_tweet_loki = Tweet(content="ROFL MOFL SHITHEADS", user_uuid=new_user.uuid)
        new_tweet_2 = Tweet(content="STILL MOFL ROFL", user_uuid=new_user.uuid)
        new_tweet_floki = Tweet(
            content="I AM NOT AGREE WITH U, DCK HD", user_uuid=new_user_2.uuid
        )
        session.add(new_tweet_loki)
        await session.commit()
        time.sleep(1)
        session.add(new_tweet_2)
        session.add(new_tweet_floki)
        await session.commit()
        new_image = Image(tweet_uuid=new_tweet_loki.uuid, source=["/static/images/cat.jpeg", "/static/images/cute.jpeg"])
        session.add(new_image)
        await session.commit()
        floki_likes_loki = Like(
            tweet_uuid=new_tweet_loki.uuid, user_uuid=new_user_2.uuid
        )
        session.add(floki_likes_loki)
        floki_reposts_loki = Repost(
            tweet_uuid=new_tweet_loki.uuid, user_uuid=new_user_2.uuid
        )
        session.add(floki_reposts_loki)
        await session.commit()
        await session.close()
    yield
    async with async_session() as session:
        await session.delete(new_tweet_loki)
        await session.commit()
    async with async_session() as session:
        await session.delete(new_tweet_2)
        await session.commit()
        await session.delete(new_tweet_floki)
        await session.commit()
        await session.delete(new_user)
        await session.delete(new_user_2)
        await session.commit()
    await session.close()
    await engine.dispose()
