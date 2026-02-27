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

# For async version (asyncpg)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
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
