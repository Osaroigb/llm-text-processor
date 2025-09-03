from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base
from app.core import get_settings, setup_logging, get_logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)

# Create base class for models
Base = declarative_base()

# Global variables for engine and session factory
_async_engine = None
_AsyncSessionLocal = None


def _get_async_engine():
    """Get or create async engine."""
    global _async_engine
    
    if _async_engine is None:
        _async_engine = create_async_engine(
            str(settings.DATABASE_URL),
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
        )
    
    return _async_engine


def _get_async_session_factory():
    """Get or create async session factory."""
    global _AsyncSessionLocal
    
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            _get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    return _AsyncSessionLocal


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""    
    async with _get_async_session_factory()() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with _get_async_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    logger.info("Closing database connections...")
    
    if _async_engine:
        await _async_engine.dispose()
        logger.info("Database connections closed")
    else:
        logger.info("No database connections to close")
