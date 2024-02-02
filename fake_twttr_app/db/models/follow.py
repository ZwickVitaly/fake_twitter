from sqlalchemy import (
    Column,
    ForeignKey,
    Uuid,
)
from fake_twttr_app.db.base import Base


class Follow(Base):
    __tablename__ = "follows"

    followed_user = Column(
        Uuid, ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True
    )
    follower_user = Column(
        Uuid, ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True
    )
