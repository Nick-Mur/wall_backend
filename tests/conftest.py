import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

if "TEST_DATABASE_URL" in os.environ:
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
else:
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://wall:wall@localhost:5433/the_wall_test")

from libs.postgres.base import Base
from libs.postgres.session import get_session
from services.message_service.infrastructure.db_models.message import MessageModel
from services.message_service.infrastructure.db_models.message_hash import MessageHashModel
from services.message_service.infrastructure.db_models.message_link import MessageLinkModel
from services.message_service.infrastructure.db_models.moderation_log import ModerationLogModel
from services.message_service.infrastructure.db_models.report import ReportModel
from services.message_service.main import app as message_app
from services.search_service.infrastructure.db_models.search_log import SearchLogModel
from services.search_service.main import app as search_app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.environ["DATABASE_URL"])

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

_MODELS = (
    MessageModel,
    MessageHashModel,
    MessageLinkModel,
    ModerationLogModel,
    ReportModel,
    SearchLogModel,
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def db_schema():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


async def clear_database() -> None:
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(delete(table))


@pytest_asyncio.fixture
async def clean_db(db_schema):
    await clear_database()
    yield
    await clear_database()


@pytest_asyncio.fixture
async def db_session(clean_db):
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def message_client(clean_db):
    message_app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=message_app)

    async with AsyncClient(transport=transport, base_url="http://message.test") as client:
        yield client

    message_app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def search_client(clean_db):
    search_app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=search_app)

    async with AsyncClient(transport=transport, base_url="http://search.test") as client:
        yield client

    search_app.dependency_overrides.pop(get_session, None)
