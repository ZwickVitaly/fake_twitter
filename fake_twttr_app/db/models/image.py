from sqlalchemy import Column, ForeignKey, Integer, String

from fake_twttr_app.db.base import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_extension = Column(
        String,
    )
    tweet_uuid = Column(
        ForeignKey("tweets.uuid", ondelete="CASCADE"),
    )
