from pydantic_settings import BaseSettings
from httpx import AsyncClient


class Settings(BaseSettings):
    """
    Settings class to manage application settings.
    """
    class Config:
        env_file = ".env"
        extra = "ignore" 
        
    CAPITAL_IDENTITY: str
    CAPITAL_PASSWORD: str
    CAPITAL_API_KEY: str
    
    session: AsyncClient = AsyncClient()
        
        
settings = Settings()

print(settings.CAPITAL_IDENTITY)