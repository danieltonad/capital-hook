from pydantic_settings import BaseSettings
from httpx import AsyncClient


class Settings(BaseSettings):
    """
    Settings class to manage application settings.
    """
    
    session: AsyncClient
    
    def __init__(self):
        self.session = AsyncClient()