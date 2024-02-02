from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, String
from sqlalchemy.orm import selectinload
from fake_twttr_app.app.auth_wrappers import auth_required_cookie
from fake_twttr_app.db.base import async_session
from fake_twttr_app.app.headers import api_key_keyword
from fake_twttr_app.db import User, Tweet, Follow, Like

users_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

templates = Jinja2Templates(directory="fake_twttr_app/static/templates")


@users_router.get("/{user_uuid:str}")
@users_router.get("/me")
@auth_required_cookie
async def get_my_info_handler(request: Request, user_uuid: Optional[str] = None):
    context = {}
    session_user_uuid = request.cookies.get("my_uuid")
    if user_uuid and session_user_uuid != user_uuid:
        key = User.uuid.cast(String).ilike(user_uuid)
    elif session_user_uuid == user_uuid:
        return RedirectResponse(f"{users_router.prefix}/me", status_code=303)
    else:
        key = User.api_key.ilike(request.cookies.get(api_key_keyword))
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
        user_reposts = [
            await repost.to_safe_json(session_user_uuid=session_user_uuid) for repost in user.user_tweet_repost
        ]
        tweets = [await tweet.to_safe_json(session_user_uuid=session_user_uuid) for tweet in user.tweets]
        my_followed = [await user.to_safe_json() for user in user.followed]
        my_followers = [await user.to_safe_json() for user in user.followers]
        tweets.extend(user_reposts)
        tweets.sort(key=lambda x: x.get("created_at"), reverse=True)
        for i, tweet in enumerate(tweets):
            if tweet.get("repost"):
                tweet["repost"]["created_at"] = tweet["repost"]["created_at"].strftime("%H:%M  %d.%m.%Y")
            else:
                tweet["created_at"] = tweet["created_at"].strftime("%H:%M  %d.%m.%Y")
    context.update(
        {
            "profile": await user.to_safe_json(),
            "tweets": tweets,
            "followed": {"quantity": len(my_followed), "followed_list": my_followed},
            "followers": {"quantity": len(my_followers), "followers_list": my_followers},
            "origin_url": users_router.prefix,
        }
    )
    if session_user_uuid != str(user.uuid):
        followers = [str(u["uuid"]) for u in my_followers]
        if session_user_uuid not in followers:
            context.update({"is_followed": False})
        else:
            context.update({"is_followed": True})
    return templates.TemplateResponse(request=request, name="user_info.html", context=context)


@users_router.post("/{followed_uuid:str}/follow")
@auth_required_cookie
async def post_follow_handler(request: Request, followed_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
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
                    Response(status_code=201)
                else:
                    raise
    return Response(status_code=201)


@users_router.delete("/{followed_uuid:str}/follow")
@auth_required_cookie
async def delete_follow_handler(request: Request, followed_uuid: str):
    async with async_session() as session:
        async with session.begin():
            user_uuid = (await User.get_user_by_api_token(request.cookies.get(api_key_keyword))).uuid
            try:
                like_q = delete(Follow).filter_by(follower_user=user_uuid, followed_user=UUID(followed_uuid))
                await session.execute(like_q)
            except ValueError:
                raise HTTPException(422, "Bad uuid")
    return Response(status_code=201)
