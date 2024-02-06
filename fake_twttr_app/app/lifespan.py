from contextlib import asynccontextmanager

from fake_twttr_app.db import Admin, Base, async_session, engine


@asynccontextmanager
async def basic_lifespan(*args, **kwargs):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    admin = Admin(login="Dezann", password="123")
    async with async_session() as session:
        session.add(admin)
        await session.commit()
    yield
    await session.close()
    await engine.dispose()
