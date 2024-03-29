"""Application lifespan module"""

from contextlib import asynccontextmanager
import logging
from getpass import getpass

from sqlalchemy import Result, select

from fake_twttr_app.db import Admin, Base, async_session, engine

from .config import logger_name


logger = logging.getLogger(logger_name)


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    logger.debug("Starting application")
    async with engine.begin() as conn:
        logger.debug("Creating database if not exists")
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        async with session.begin():
            logger.debug("Checking if there is admin")
            query: Result[tuple[Admin]] = await session.execute(
                select(Admin)
            )
            existing_admin = query.scalar_one_or_none()
            if not existing_admin:
                logger.warning("No admin detected. Creating a new one.")
                admin = Admin(
                    login=input("\033[1;33mInput superuser login: \033[0m"),
                    password=getpass("\033[1;33mInput superuser password: \033[0m")
                )
                session.add(admin)
                logger.debug("Created admin")
                await session.commit()
    logger.debug("Application started working")
    yield
    logger.debug("Shutting down app")
    await session.close()
    await engine.dispose()
