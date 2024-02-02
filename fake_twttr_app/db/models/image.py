from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY

from fake_twttr_app.db.base import Base


class Image(Base):
    __tablename__ = "images"

    uuid = Column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tweet_uuid = Column(ForeignKey("tweets.uuid", ondelete="CASCADE"), nullable=False)
    source = Column(ARRAY(String), nullable=False)