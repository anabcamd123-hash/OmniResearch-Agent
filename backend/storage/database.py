import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./omni.db",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
