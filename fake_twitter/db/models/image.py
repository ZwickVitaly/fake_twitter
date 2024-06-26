"""
Image sqlalchemy model
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from fake_twitter.db import Base


class Image(Base):
    __tablename__ = "images"

    id: Column[int] = Column(Integer, primary_key=True, autoincrement=True)
    file_extension = Column(
        String,
    )
    tweet_id: Column[int] = Column(
        ForeignKey("tweets.id", ondelete="CASCADE"),
    )
