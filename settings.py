from pydantic_settings import BaseSettings
from httpx import AsyncClient
from enums.trade import TradeMode


class Settings(BaseSettings):
    """
    Settings class to manage application settings.
    """
    class Config:
        env_file = ".env"
        extra = "ignore" 
        
    #
    CAPITAL_IDENTITY: str
    CAPITAL_PASSWORD: str
    CAPITAL_API_KEY: str
    
    MODE: TradeMode
    
    CAPITAL_HOST_LIVE = "https://api-capital.backend-capital.com"
    CAPITAL_HOST_DEMO = "https://demo-api-capital.backend-capital.com"
    
    TRADINGVIEW_IP_ADDRESS : list = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]
    
    session: AsyncClient = AsyncClient()
    
    
    def update_trade_mode(self, mode: TradeMode):
        self.MODE = mode
    
    def get_capital_host(self) -> str:
        if self.MODE == TradeMode.LIVE:
            return self.CAPITAL_HOST_LIVE
        return self.CAPITAL_HOST_DEMO
    
        
        
settings = Settings()