"""
User sqlalchemy model
"""

from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Index,
    Integer,
    String,
    select,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from fake_twitter.db import Base, async_session

from .tweet import Tweet


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("char_length(name) > 2", name="name_min_length"),)

    id = Column(Integer, primary_key=True)
    name = Column(
        String(
            50,
            collation="C",
        ),
        nullable=False,
    )
    api_key = Column(
        String,
        nullable=False,
        unique=True,
    )
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp()
    )
    index = Index(
        "unique_username",
        func.upper(name),
        unique=True,
    )

    followed = relationship(
        "User",
        secondary="follows",
        primaryjoin="Follow.follower_user == User.id",
        secondaryjoin="Follow.followed_user == User.id",
        backref=backref("followers", lazy="joined"),
        lazy="selectin",
    )
    tweets = relationship(
        "Tweet",
        lazy="joined",
        cascade="all, delete-orphan",
        foreign_keys="Tweet.user_id",
        back_populates="tweet_author",
        order_by=lambda: Tweet.__table__.columns.created_at.desc(),
    )

    user_likes = relationship(
        "Like",
        back_populates="user",
        lazy="noload",
        cascade="all, delete-orphan",
        foreign_keys="Like.user_id",
    )
    user_tweet_repost = relationship(
        "Repost",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    reposted_tweets = association_proxy(
        "user_tweet_repost",
        "reposted_tweet",
    )

    def __repr__(self):
        return f"User: {self.name}"

    def to_json(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    async def to_safe_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    @classmethod
    async def get_user_by_api_token(cls, api_token):
        async with async_session() as session:
            user = await session.execute(
                select(cls).filter_by(api_key=api_token, active=True)
            )
        return user.unique().scalar_one_or_none()

    @classmethod
    async def get_user_by_id(cls, user_id):
        async with async_session() as session:
            user = await session.execute(select(cls).filter_by(id=user_id, active=True))
        return user.unique().scalar_one_or_none()

    @classmethod
    async def get_user_by_name(cls, name):
        async with async_session() as session:
            user = await session.execute(select(cls).filter_by(name=name, active=True))
        return user.unique().scalar_one_or_none()
