import os
from httpx import AsyncClient
from enums.trade import TradeMode
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """
    Settings class to manage application settings.
    """
            
    CAPITAL_HOST_LIVE: str = "https://api-capital.backend-capital.com"
    CAPITAL_HOST_DEMO: str = "https://demo-api-capital.backend-capital.com"
    
    #
    CAPITAL_IDENTITY: str = os.getenv("CAPITAL_IDENTITY")
    CAPITAL_PASSWORD: str = os.getenv("CAPITAL_PASSWORD")
    CAPITAL_API_KEY: str =  os.getenv("CAPITAL_API_KEY")
    
    TRADE_MODE: TradeMode
    
    TRADINGVIEW_IP_ADDRESS : list = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]
    
    session: AsyncClient = AsyncClient()
    
    
    def update_trade_mode(self, trade_mode: TradeMode):
        self.TRADE_MODE = trade_mode
    
    def get_capital_host(self) -> str:
        return self.CAPITAL_HOST_LIVE if self.TRADE_MODE == TradeMode.LIVE else self.CAPITAL_HOST_DEMO
    
        
        
settings = Settings()