import aiosqlite
from enums.trade import TradeMode

async def create_connection() -> aiosqlite.Connection:
    from memory import settings
    return await aiosqlite.connect(settings.DB_PATH)


# migrate database
async def migrate_db() -> None:
    from memory import settings
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
            
            # positions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id TEXT PRIMARY KEY,
                    epic TEXT NOT NULL,
                    size REAL NOT NULL,
                    hook_name TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    exit_criteria TEXT NOT NULL,
                    profit_price REAL NOT NULL,
                    loss_price REAL NOT NULL,
                    trail_sl INTEGER NOT NULL,
                    mode TEXT NOT NULL
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
        
        
        
        
async def save_trade_history(trade_id: str, epic: str, size: float, pnl: float, pnl_percentage: float, direction: str, exit_type: str, hook_name: str, entry_price: float, exit_price: float, opened_at: str, closed_at: str, mode: TradeMode) -> None:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO trades (id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, mode)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    trade_id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, mode.value
                ))
        await db.commit()


async def get_trade_history(mode: TradeMode = None ) -> list:
    from memory import memory, settings
    from utils import datetime_format
    mode = settings.TRADE_MODE if not mode else mode
    trades = []
    profits = 0
    losses = 0
    spreads = 0
    pnl = 0.0
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM trades WHERE mode = ? ORDER BY closed_at DESC",
                (mode.value,)
            )
            rows = await cursor.fetchall()
            for row in rows:
                id, epic, size, pnl, pnl_percentage, direction, exit_type, hook_name, entry_price, exit_price, opened_at, closed_at, mode = row
                if pnl > 0:
                    profits += pnl
                elif pnl < 0:
                    losses += abs(pnl)
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
            
            pnl = profits - losses - spreads
            return {
                "trades": trades,
                "profits": f"+{profits:,.2f}",
                "losses": f"-{losses:,.2f}",
                "spreads": f"-{spreads:,.2f}",
                "pnl": f"{pnl:,.2f}",
                "count": len(trades)
            }
        

async def update_trade_mode_db(mode: TradeMode) -> None:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            # Check if a config row exists
            await cursor.execute("SELECT id FROM bot_config ORDER BY id DESC LIMIT 1")
            row = await cursor.fetchone()
            if row:
                # Update the latest config
                await cursor.execute(
                    """
                    UPDATE bot_config
                    SET trade_mode = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (mode.value, row[0])
                )
            else:
                # Insert new config
                await cursor.execute(
                    """
                    INSERT INTO bot_config (trade_mode, created_at, updated_at)
                    VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (mode.value,)
                )
        await db.commit()


async def get_trade_mode() -> TradeMode:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT trade_mode FROM bot_config ORDER BY id DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            if row:
                return TradeMode(row[0])
            else:
                return TradeMode.DEMO
            


async def get_positions() -> list:
    from memory import settings
    from enums.trade import ExitType
    from model import PositionsModel
    positions = []
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM positions ORDER BY entry_date DESC"
            )
            rows = await cursor.fetchall()
            for row in rows:
                id, epic, size, hook_name, direction, entry_price, entry_date, exit_criteria, profit_price, loss_price, trail_sl, mode = row
                position = {
                    "id": id,
                    "epic": epic,
                    "size": float(size),
                    "hook_name": hook_name,
                    "direction": direction,
                    "entry_price": entry_price,
                    "entry_date": entry_date,
                    "exit_criteria": [ExitType(e.strip()) for e in exit_criteria.split(",")],
                    "profit_price": profit_price,
                    "loss_price": loss_price,
                    "trail_sl": trail_sl,
                    "mode": mode
                }
                positions.append(PositionsModel(**position))
    return positions


async def save_position(id: str, epic: str, size: float, hook_name: str, direction: str, entry_price: float, entry_date: str, exit_criteria: str, profit_price: float, loss_price: float, trail_sl: int, mode: TradeMode) -> None:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO positions (id, epic, size, hook_name, direction, entry_price, entry_date, exit_criteria, profit_price, loss_price, trail_sl, mode)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?) 
                """, (
                    id, epic, size, hook_name, direction, entry_price, entry_date, exit_criteria, profit_price, loss_price, trail_sl, mode.value
                ))
        await db.commit()



async def delete_position(position_id: str) -> None:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM positions WHERE id = ?
                """, (
                    position_id,
                ))
        await db.commit()



async def clear_config() -> None:
    from memory import settings
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute("DELETE FROM bot_config")
        await db.commit()