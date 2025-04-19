import aiosqlite
from settings import settings

async def create_connection():
    return await aiosqlite.connect(settings.DB_PATH)