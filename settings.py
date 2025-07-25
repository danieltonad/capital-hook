import os
from aiosqlite import Connection
from httpx import AsyncClient
from enums.trade import TradeMode
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """
    Settings class to manage application settings.
    """
    
    APP_TITLE = "Capital Hook"
    DB_PATH = "database.db"
    DB_CONNECTION: Connection = None

    CAPITAL_HOST_LIVE: str = "https://api-capital.backend-capital.com"
    CAPITAL_HOST_DEMO: str = "https://demo-api-capital.backend-capital.com"
    CAPITAL_WSS_HOST: str = "wss://api-streaming-capital.backend-capital.com/connect"
    
    #
    CAPITAL_IDENTITY: str = os.getenv("CAPITAL_IDENTITY")
    CAPITAL_PASSWORD: str = os.getenv("CAPITAL_PASSWORD")
    CAPITAL_API_KEY: str =  os.getenv("CAPITAL_API_KEY")
    
    TRADE_MODE: TradeMode
    
    TRADINGVIEW_IP_ADDRESS : list = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7", "127.0.0.1"]
    
    session: AsyncClient = AsyncClient() # HTTP session initialization
    
    capital_socket_service = None # capital socket initialization

    async def sync_trade_mode(self):
        from database import get_trade_mode
        self.TRADE_MODE = await get_trade_mode()


    async def update_trade_mode(self, trade_mode: TradeMode):
        from database import update_trade_mode_db
        self.TRADE_MODE = trade_mode
        await update_trade_mode_db(trade_mode)

    def get_capital_host(self, mode: TradeMode = None) -> str:
        if mode:
            return self.CAPITAL_HOST_LIVE if mode == TradeMode.LIVE else self.CAPITAL_HOST_DEMO
        
        return self.CAPITAL_HOST_LIVE if self.TRADE_MODE == TradeMode.LIVE else self.CAPITAL_HOST_DEMO
    
        
        
settings = Settings()