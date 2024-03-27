from contextlib import asynccontextmanager
import logging
from getpass import getpass

from sqlalchemy import Result, select

from fake_twttr_app.db import Admin, Base, async_session, engine


logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        async with session.begin():
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
                await session.commit()
    yield
    await session.close()
    await engine.dispose()
