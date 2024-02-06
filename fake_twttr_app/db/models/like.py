from typing import Any

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from fake_twttr_app.db.base import Base


class Like(Base):
    __tablename__ = "likes"

    tweet_uuid = Column(ForeignKey("tweets.uuid"), nullable=False, primary_key=True)
    user_uuid = Column(ForeignKey("users.uuid"), nullable=False, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=0), server_default=func.current_timestamp()
    )

    def to_json(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
