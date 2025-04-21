import aiosqlite
from settings import settings

async def create_connection() -> aiosqlite.Connection:
    return await aiosqlite.connect(settings.DB_PATH)

# migrate database
async def migrate_db():
    async with settings.DB_CONNECTION.cursor() as cursor:
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY ,
                epic TEXT NOT NULL,
                size REAL NOT NULL,
                direction TEXT NOT NULL,
                deal_id TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
        """)
        await settings.DB_CONNECTION.commit()