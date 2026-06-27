import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL","postgresql+asyncpg://wall:wall@localhost:5433/the_wall_test",)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
