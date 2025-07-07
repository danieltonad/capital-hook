import aiosqlite
from settings import settings
from enums.trade import TradeMode

async def create_connection() -> aiosqlite.Connection:
    return await aiosqlite.connect(settings.DB_PATH)


# migrate database
async def migrate_db() -> None:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            # trades table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    epic TEXT NOT NULL,
                    size REAL NOT NULL,
                    pnl REAL NOT NULL,
                    pnl_percentage REAL NOT NULL,
                    direction TEXT NOT NULL,
                    exit_type TEXT NOT NULL,
                    hook_name TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    opened_at TEXT NOT NULL,
                    closed_at TEXT NOT NULL,
                    mode TEXT NOT NULL
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
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        await db.commit()
        
        
        
        
async def insert_trade_history(trade_id: str, epic: str, size: float, pnl: float, pnl_percentage: float, direction: str, exit_type: str, hook_name: str, entry_price: float, exit_price: float, opened_at: str, closed_at: str) -> None:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO trades (id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, mode)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    trade_id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, settings.TRADE_MODE.value
                ))
        await db.commit()


async def get_trade_history() -> list:
    from utils import datetime_format
    from memory import memory
    trades = []
    profits = 0
    loasses = 0
    spreads = 0
    pnl = 0.0
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM trades WHERE mode = ?", (settings.TRADE_MODE.value,))
            rows = await cursor.fetchall()
            for row in rows:
                id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, mode = row
                if pnl > 0:
                    profits += pnl
                elif pnl < 0:
                    loasses += abs(pnl)
                spreads += abs(exit_price - entry_price) * (size / memory.get_leverage(epic))  # assuming spread is calculated as the difference between exit and entry price times size
                trade = {
                    "id": id,
                    "epic": epic,
                    "size": size,
                    "pnl": f"{pnl:,.2f}",
                    "pnl_percentage": f"{pnl_percentage:,.2f}%",
                    "direction": direction,
                    "exit_type": exit_type,
                    "hook_name": hook_name,
                    "entry_price": f"{entry_price:,}",
                    "exit_price": f"{exit_price:,}",
                    "opened_at": datetime_format(opened_at),
                    "closed_at": datetime_format(closed_at),
                    "mode": mode
                }
                trades.append(trade)
            
            pnl = profits - loasses - spreads
            return {
                "trades": trades,
                "profits": f"+{profits:,.2f}",
                "loasses": f"-{loasses:,.2f}",
                "spreads": f"-{spreads:,.2f}",
                "pnl": f"{pnl:,.2f}",
                "count": len(trades)
            }


async def save_failed_hooks(hook_id: str, epic: str, hook_name: str, direction: str, error_message: str, created_at: str) -> None:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
            """
            INSERT INTO failed_hooks (id, epic, hook_name, direction, error_message, created_at)
            VALUES (?,?,?,?,?,?)
            """, (
                hook_id, epic, hook_name, direction, error_message, created_at
            ))
        await db.commit()