"""Application lifespan module"""

import logging
from contextlib import asynccontextmanager
from os import getenv

from sqlalchemy import select

from fake_twitter.db import Admin, Base, async_session, engine

from .config import logger_name

logger = logging.getLogger(logger_name)


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    """
    Basic lifespan function.

    Creates database if it doesn't exist

    Checks if there is admin

    If not - initiates creation of new one

    If there is admin - yields to app process

    Before shutdown closes session and disposes database engine
    """
    logger.debug("Starting application")
    async with engine.begin() as conn:
        logger.debug("Creating database if not exists")
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        async with session.begin():
            logger.debug("Checking if there is admin")
            query = await session.execute(select(Admin))
            existing_admin = query.scalar_one_or_none()
            if not existing_admin:
                logger.warning("No admin detected. Creating a new one.")
                admin = Admin(
                    login=getenv("ADMIN_LOGIN") or "admin",
                    password=getenv("ADMIN_PASSWORD") or "admin",
                )
                session.add(admin)
                logger.debug("Created admin")
                await session.commit()
    logger.debug("Application started working")
    yield
    logger.debug("Shutting down app")
    await session.close()
    await engine.dispose()
