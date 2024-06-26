"""
Follow sqlalchemy model
"""

from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP

from fake_twitter.db import Base


class Follow(Base):
    __tablename__ = "follows"

    followed_user: Column[int] | int = Column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    follower_user: Column[int] | int = Column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )
