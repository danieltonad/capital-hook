import aiosqlite
from settings import settings

async def create_connection() -> aiosqlite.Connection:
    return aiosqlite.connect(settings.DB_PATH)

# migrate database
async def migrate_db() -> None:
    async with settings.DB_CONNECTION as cursor:
        # trades table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY ,
                epic TEXT NOT NULL,
                leverage TEXT NOT NULL,
                size REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_percentage REAL NOT NULL,
                direction TEXT NOT NULL,
                exit_type TEXT NOT NULL,
                hook_name TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                opened_at TEXT NOT NULL,
                closed_at TEXT NOT NULL
            )
        """)
        
        # failed hooks table
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS failed_hooks (
                id TEXT PRIMARY KEY,
                epic TEXT NOT NULL,
                hook_name TEXT NOT NULL,
                direction TEXT NOT NULL,
                error_message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await settings.DB_CONNECTION.commit()