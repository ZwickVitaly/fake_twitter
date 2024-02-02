from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, String
from sqlalchemy.orm import selectinload
from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.db.base import async_session
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User, Tweet, Follow, Like


api_users_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@api_users_router.get("/me")
@api_users_router.get("/{user_uuid:str}")
@auth_required_header
async def get_my_info_handler(request: Request, user_uuid: Optional[str] = None):
    if user_uuid:
        key = User.uuid.cast(String).ilike(user_uuid)
    else:
        key = User.api_key.ilike(request.headers.get(api_key_keyword))
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(User)
                .options(selectinload(User.user_tweet_repost))
                .options(
                    selectinload(User.tweets).options(
                        selectinload(Tweet.user_tweet_repost)
                    )
                )
                .options(selectinload(User.followed))
                .options(selectinload(User.followers))
                .filter(key)
            )
        user = user.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User does not exist")
        my_reposts = [
            repost.to_safe_json() for repost in user.user_tweet_repost
        ]
        tweets = [tweet.to_safe_json() for tweet in user.tweets]
        my_followed = [user.to_safe_json() for user in user.followed]
        my_followers = [user.to_safe_json() for user in user.followers]
        tweets.extend(my_reposts)
        tweets.sort(key=lambda x: x.get("created_at"), reverse=True)

    return {
        "profile": user.to_safe_json(),
        "tweets": tweets,
        "followed": my_followed,
        "followers": my_followers,
    }


@api_users_router.post("/{followed_uuid:str}/follow")
@auth_required_header
async def post_follow_handler(request: Request, followed_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.headers.get(api_key_keyword))).uuid
            if str(user_uuid) == followed_uuid:
                raise HTTPException(403, "You can't follow yourself. THAT'S LIFE DUDE!")
            try:
                new_follow = Follow(follower_user=user_uuid, followed_user=UUID(followed_uuid))
                session.add(new_follow)
                await session.commit()
            except ValueError:
                raise HTTPException(422, "Bad uuid")
            except IntegrityError as e:
                if e.orig.pgcode == "23503":
                    raise HTTPException(404, "User does not exist")
                elif e.orig.pgcode == "23505":
                    raise HTTPException(403, "You are already following this user")
                else:
                    raise
    return {"result": True}


@api_users_router.delete("/{followed_uuid:str}/follow")
@auth_required_header
async def delete_follow_handler(request: Request, followed_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.headers.get("api-key"))).uuid
            try:
                like_q = delete(Like).filter_by(user_uuid=user_uuid, tweet_uuid=UUID(followed_uuid))
                await session.execute(like_q)
            except ValueError:
                raise HTTPException(422, "Bad uuid")
    return {"result": True}
