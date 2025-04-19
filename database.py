import aiosqlite
from settings import settings

async def create_connection() -> aiosqlite.Connection:
    return await aiosqlite.connect(settings.DB_PATH)