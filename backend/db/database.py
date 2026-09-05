"""
Database connection management.
Supports SQLite (portable) and PostgreSQL (full).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from loguru import logger
from config.settings import settings


# Async engine (FastAPI / async routes)
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine (Alembic migrations)
sync_engine = create_engine(
    settings.database_url_sync,
    echo=False,
    future=True,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (used on startup when not using Alembic)."""
    from backend.db.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Database initialized [{settings.db_mode}]: {settings.database_url}")
