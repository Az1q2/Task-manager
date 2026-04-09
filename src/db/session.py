from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine, text
from core.config import settings

sync_engine = create_engine(
    url = settings.database_url_psycopg,
    echo = True
)
async_engine = create_engine(
    url = settings.database_url_asyncpg,
    echo = True
)
