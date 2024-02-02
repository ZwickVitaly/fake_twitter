from typing import Any

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Uuid,
    text,
    select
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from fake_twttr_app.db.base import async_session
from fake_twttr_app.db.base import Base
from .like import Like
from .repost import Repost


class Tweet(Base):
    __tablename__ = "tweets"

    uuid = Column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    content = Column(String(280), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    user_uuid = Column(ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )

    # relationships
    tweet_likes = relationship(
        "Like",
        backref="tweet",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    user_tweet_repost = relationship(
        "Repost",
        back_populates="reposted_tweet",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    tweet_author = relationship(
        "User", back_populates="tweets", lazy="selectin", foreign_keys="Tweet.user_uuid"
    )
    images_urls = relationship(
        "Image", backref="tweet", lazy="selectin", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self):
        return (
            f"Твит: {self.content[:30]}..."
            if len(str(self.content)) > 30
            else f"Твит: {self.content}"
        )

    async def to_safe_json(self, session_user_uuid: str | None = None) -> dict[str, Any]:
        result = {
            "uuid": self.uuid,
            "author": await self.tweet_author.to_safe_json(),
            "content": self.content,
            "views": self.views,
            "likes": self.likes_count,
            "reposts": self.reposts_count,
            "images": self.images_urls.source if self.images_urls else [],
            "created_at": self.created_at,
            "liked_by_user": await self.done_by_user(user_uuid=session_user_uuid, search_type="Like"),
            "reposted_by_user": await self.done_by_user(user_uuid=session_user_uuid, search_type="Repost"),
        }
        return result

    async def done_by_user(self, user_uuid: str | None = None, search_type: str | None = None):
        if user_uuid is None or search_type is None:
            return None
        types = {"Like": Like, "Repost": Repost}
        if search_type not in types:
            raise ValueError("Wrong type")
        async with async_session() as session:
            search_filter = types[search_type].user_uuid.cast(String).ilike(user_uuid)
            user = await session.execute(
                select(types[search_type]).filter(search_filter).filter_by(tweet_uuid=self.uuid)
            )
        return user.unique().scalar_one_or_none() is not None

    @hybrid_property
    def likes_count(self):
        return len(self.tweet_likes)

    @hybrid_property
    def reposts_count(self):
        return len(self.user_tweet_repost)
