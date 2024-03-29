"""
Repost sqlalchemy model
"""

from typing import Any

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fake_twttr_app.db.base import Base


class Repost(Base):
    __tablename__ = "reposts"

    id = Column(Integer, primary_key=True)
    tweet_id = Column(ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )

    unique_repost = Index("unique_repost_index", tweet_id, user_id, unique=True)

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

    async def to_safe_json(self, session_user_id: int | None = None):
        return {
            "id": self.id,
            "repost": await self.reposted_tweet.to_safe_json(
                session_user_id=session_user_id
            ),
            "created_at": self.created_at,
        }
