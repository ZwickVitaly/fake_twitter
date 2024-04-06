"""
Tweet sqlalchemy model
"""

from typing import Any

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fake_twitter.app.config import static_request_path
from fake_twitter.db import Base


class Tweet(Base):
    __tablename__ = "tweets"
    id: Column[int] = Column(Integer, primary_key=True)
    content = Column(String(280), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    user_id: Column[int] = Column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
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
        "User", back_populates="tweets", lazy="selectin", foreign_keys="Tweet.user_id"
    )
    images_objects = relationship(
        "Image",
        backref="tweet",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"Твит: {self.content[:30]}..."
            if len(str(self.content)) > 30
            else f"Твит: {self.content}"
        )

    async def to_safe_json(self, session_user_id: int | None = None) -> dict[str, Any]:
        result = {
            "id": self.id,
            "author": await self.tweet_author.to_safe_json(),
            "content": self.content,
            "views": self.views,
            "likes": [await like.user.to_safe_json() for like in self.tweet_likes],
            # "reposts": self.reposts_count,
            "attachments": [
                f"{static_request_path}/{image.id}{image.file_extension}"
                for image in self.images_objects
            ],
            "created_at": self.created_at,
        }
        if session_user_id:
            html_extra = {
                "liked_by_user": await self.done_by_user(
                    user_id=session_user_id, search_type="Like"
                ),
                "reposted_by_user": await self.done_by_user(
                    user_id=session_user_id, search_type="Repost"
                ),
            }
            result.update(html_extra)
        return result

    @hybrid_property
    def likes_count(self):
        return len(self.tweet_likes)

    # @hybrid_property
    # def reposts_count(self):
    #     return len(self.user_tweet_repost)
