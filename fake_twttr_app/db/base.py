"""
Module of base sqlalchemy settings
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

engine = create_async_engine("postgresql+asyncpg://admin:admin@postgres:5432")
Base = declarative_base()
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
