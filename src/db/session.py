from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.db.base import Base

from src.modules.users.models import User
from src.modules.tasks.models import Task


sync_engine = create_engine(
    url = settings.database_url_psycopg,
    echo = True
)
async_engine = create_async_engine(
    url = settings.database_url_asyncpg,
    echo = True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


