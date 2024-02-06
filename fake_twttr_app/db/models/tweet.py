from typing import Any

from sqlalchemy import Column, ForeignKey, Integer, String, Uuid, select, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fake_twttr_app.app.folders import static_request_path
from fake_twttr_app.db.base import Base, async_session

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

    async def to_safe_json(
        self, session_user_uuid: str | None = None
    ) -> dict[str, Any]:
        result = {
            "uuid": self.uuid,
            "author": await self.tweet_author.to_safe_json(),
            "content": self.content,
            "views": self.views,
            "likes": self.likes_count,
            "reposts": self.reposts_count,
            "images": [
                f"{static_request_path}/{image.id}{image.file_extension}"
                for image in self.images_objects
            ],
            "created_at": self.created_at,
        }
        if session_user_uuid:
            html_extra = {
                "liked_by_user": await self.done_by_user(
                    user_uuid=session_user_uuid, search_type="Like"
                ),
                "reposted_by_user": await self.done_by_user(
                    user_uuid=session_user_uuid, search_type="Repost"
                ),
            }
            result.update(html_extra)
        return result

    async def done_by_user(
        self, user_uuid: str | None = None, search_type: str | None = None
    ):
        if user_uuid is None or search_type is None:
            return None
        search_types = {"Like": Like, "Repost": Repost}
        if search_type not in search_types:
            raise ValueError("Wrong type")
        async with async_session() as session:
            search_filter = (
                search_types[search_type].user_uuid.cast(String).ilike(user_uuid)
            )
            user = await session.execute(
                select(search_types[search_type])
                .filter(search_filter)
                .filter_by(tweet_uuid=self.uuid)
            )
        return user.unique().scalar_one_or_none() is not None

    @hybrid_property
    def likes_count(self):
        return len(self.tweet_likes)

    @hybrid_property
    def reposts_count(self):
        return len(self.user_tweet_repost)
