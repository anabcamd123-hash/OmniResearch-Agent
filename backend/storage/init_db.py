from .database import engine
from .models import Base


async def init_db():

    async with engine.begin() as conn:
        # 启用 WAL 模式，提升并发性能
        await conn.exec_driver_sql(
            "PRAGMA journal_mode=WAL"
        )
        await conn.run_sync(
            Base.metadata.create_all
        )
