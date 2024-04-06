"""
Admin sqlalchemy model
"""

from sqlalchemy import Column, String, select
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from fake_twitter.db import Base, async_session


class Admin(Base):
    __tablename__ = "admin"

    login = Column(
        String(
            50,
        ),
        nullable=False,
        primary_key=True,
    )
    password = Column(
        String,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True, precision=1), server_default=func.current_timestamp()
    )

    @classmethod
    async def is_admin(cls, login: str, password: str):
        async with async_session() as session:
            user = await session.execute(
                select(cls).filter_by(login=login, password=password)
            )
        return bool(user.unique().scalar_one_or_none())
