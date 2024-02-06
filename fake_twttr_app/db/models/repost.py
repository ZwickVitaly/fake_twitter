from typing import Any

from sqlalchemy import Column, ForeignKey, Index, Uuid, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fake_twttr_app.db.base import Base


class Repost(Base):
    __tablename__ = "reposts"

    uuid = Column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tweet_uuid = Column(ForeignKey("tweets.uuid", ondelete="CASCADE"), nullable=False)
    user_uuid = Column(ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )

    unique_repost = Index("unique_repost_index", tweet_uuid, user_uuid, unique=True)

    user = relationship(
        "User",
        back_populates="user_tweet_repost",
        lazy="selectin",
    )
    reposted_tweet = relationship(
        "Tweet",
        back_populates="user_tweet_repost",
        lazy="selectin",
    )

    def to_json(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    async def to_safe_json(self, session_user_uuid: str | None = None):
        return {
            "uuid": self.uuid,
            "repost": await self.reposted_tweet.to_safe_json(
                session_user_uuid=session_user_uuid
            ),
            "created_at": self.created_at,
        }
