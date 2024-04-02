"""
Like sqlalchemy model
"""

from typing import Any

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fake_twitter.db import Base


class Like(Base):
    __tablename__ = "likes"

    tweet_id: Column[int] = Column(
        ForeignKey("tweets.id"), nullable=False, primary_key=True
    )
    user_id: Column[int] = Column(
        ForeignKey("users.id"), nullable=False, primary_key=True
    )
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )

    user = relationship(
        "User",
        back_populates="user_likes",
        lazy="selectin",
        cascade="save-update, merge",
    )

    def to_json(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
