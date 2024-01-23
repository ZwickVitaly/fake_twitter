from typing import Any


from sqlalchemy import Column, ForeignKey, Integer, String, Uuid, Boolean, select, text, Computed

from sqlalchemy.sql import func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import TIMESTAMP

from sqlalchemy.orm import relationship, backref

from .base import Base, async_session


class User(Base):
    __tablename__ = "users"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    display_name = Column(String(50), nullable=False, unique=True)
    api_key = Column(String, nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # relationships
    followed = relationship(
        "User",
        secondary="follows",
        primaryjoin="Follows.follower_user == User.uuid",
        secondaryjoin="Follows.followed_user == User.uuid",
        backref=backref('followers', lazy='joined'),
        lazy="joined"
    )
    tweets = relationship("Tweet", lazy="joined", cascade="all, delete-orphan", foreign_keys="Tweet.user_uuid")
    likes = relationship("Like", lazy="noload", cascade="all, delete-orphan", foreign_keys="Like.user_uuid")
    user_tweet_repost = relationship(
        "Repost",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reposted_tweets = association_proxy(
        "user_tweet_repost",
        "reposted_tweet",
    )

    def __repr__(self):
        return f"Пользователь {self.username}"

    def to_json(self) -> dict[str, Any]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def my_reposts(self):
        return self.reposts

    @classmethod
    async def get_user_by_api_token(cls, token):
        async with async_session() as session:
            user = await session.execute(select(cls).filter_by(api_key=token))
        return user.scalars().first()


class Tweet(Base):
    __tablename__ = "tweets"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    content = Column(String(280), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    image = Column(ForeignKey("images.uuid"), nullable=True)
    user_uuid = Column(ForeignKey(User.uuid), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # relationships
    likes = relationship("Like", backref="tweet", lazy="joined", cascade="all, delete-orphan",)
    user_tweet_repost = relationship(
        "Repost",
        back_populates="reposted_tweet",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self):
        return f"Твит: {self.content[:30]}..." if len(str(self.content)) > 30 else f"Твит: {self.content}"

    def to_json(self) -> dict[str, Any]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def to_safe_json(self, user_uuid: str | bytes) -> dict[str, Any]:
        result = {
            "content": self.content,
            "views": self.views,
            "likes": len(self.likes),
            "reposts": len(self.user_tweet_repost),
            "created_at": self.created_at,
            "reposted": False
        }
        if self.image:
            result.update({"image": self.image})
        if self.user_uuid != user_uuid:
            result.update({"reposted": True})
        return result


class Image(Base):
    __tablename__ = "images"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    source = Column(String, nullable=False)


class Like(Base):
    __tablename__ = "likes"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tweet_uuid = Column(ForeignKey(Tweet.uuid), nullable=False)
    user_uuid = Column(ForeignKey(User.uuid), nullable=False)

    def to_json(self) -> dict[str, Any]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Repost(Base):
    __tablename__ = "reposts"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tweet_uuid = Column(ForeignKey(Tweet.uuid), nullable=False)
    user_uuid = Column(ForeignKey(User.uuid), nullable=False)
    user = relationship(
        User,
        back_populates="user_tweet_repost",
        lazy="joined"
    )
    reposted_tweet = relationship(
        Tweet,
        back_populates="user_tweet_repost",
        lazy="joined"
    )

    def to_json(self) -> dict[str, Any]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def get_tweet(self):
        return self.tweet


class Follows(Base):
    __tablename__ = "follows"

    uuid = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    followed_user = Column(Uuid, ForeignKey(User.uuid, ondelete="CASCADE"), nullable=False)
    follower_user = Column(Uuid, ForeignKey(User.uuid, ondelete="CASCADE"), nullable=False)
