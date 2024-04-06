"""
Module of base sqlalchemy settings
"""
from os import getenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from fake_twitter.app.config import POSTGRES_URL

engine = create_async_engine(f"postgresql+asyncpg:{POSTGRES_URL}")
Base = declarative_base()
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
