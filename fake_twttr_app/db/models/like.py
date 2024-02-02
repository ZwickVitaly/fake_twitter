from typing import Any

from sqlalchemy import (
    Column,
    ForeignKey,
    Uuid,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from fake_twttr_app.db.base import Base


class Like(Base):
    __tablename__ = "likes"

    uuid = Column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tweet_uuid = Column(ForeignKey("tweets.uuid"), nullable=False)
    user_uuid = Column(ForeignKey("users.uuid"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )
    unique_like = Index(
        "unique_like_index",
        tweet_uuid, user_uuid,
        unique=True
    )

    def to_json(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }