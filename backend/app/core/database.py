from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/masal_fabrikasi"
)

# For async: PostgreSQL -> asyncpg, SQLite -> aiosqlite (for tests)
if "sqlite" in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create engines (SQLite: check_same_thread=False for test compatibility)
_engine_kw = dict(echo=False, pool_pre_ping=True)
if "sqlite" in DATABASE_URL:
    _engine_kw["connect_args"] = {"check_same_thread": False}
    _engine_kw["pool_size"] = _engine_kw["max_overflow"] = 0
else:
    _engine_kw["pool_size"] = 20
    _engine_kw["max_overflow"] = 10

engine = create_engine(DATABASE_URL, **_engine_kw)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5 if "sqlite" not in DATABASE_URL else 0,
    max_overflow=10 if "sqlite" not in DATABASE_URL else 0,
)

# Setup query performance monitoring
if os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true":
    from app.core.query_monitor import setup_query_logging
    setup_query_logging(engine)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

from sqlalchemy.orm import declarative_base

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """Dependency for getting database session in FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Async version for async endpoints."""
    async with AsyncSessionLocal() as session:
        yield session
