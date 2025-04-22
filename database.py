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
        
        # bot config
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_mode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await settings.DB_CONNECTION.commit()
        
        
        
        
async def saved_trade_history(trade_id: str, epic: str, leverage: str, size: float, pnl: float, pnl_percentage: float, direction: str, exit_type: str, hook_name: str, entry_price: float, exit_price: float, opened_at: str, closed_at: str) -> None:
    async with settings.DB_CONNECTION as cursor:
        await cursor.execute(
            """
            INSERT INTO trades (id, epic, leverage, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                trade_id, epic, leverage, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at
            ))
        await settings.DB_CONNECTION.commit()
        
        
async def saved_failed_hooks(hook_id: str, epic: str, hook_name: str, direction: str, error_message: str, created_at: str) -> None:
    async with settings.DB_CONNECTION as cursor:
        await cursor.execute(
            """
            INSERT INTO failed_hooks (id, epic, hook_name, direction, error_message, created_at)
            VALUES (?,?,?,?,?,?)
            """, (
                hook_id, epic, hook_name, direction, error_message, created_at
            ))
        await settings.DB_CONNECTION.commit()