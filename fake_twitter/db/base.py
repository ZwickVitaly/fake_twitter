"""
Module of base sqlalchemy settings
"""
from os import getenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

engine = create_async_engine(
    f"postgresql+asyncpg://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@postgres:5432"
)
Base = declarative_base()
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
