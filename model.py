from pydantic import BaseModel, conint
from enums.trade import TradeDirection
from typing import Annotated


class TradingViewWebhookModel(BaseModel):
    epic: str
    direction: TradeDirection
    amount: Annotated[int, conint(ge=5)] 
    hook_name: str
    profit: Annotated[int, conint(ge=1)] 
    loss: Annotated[int, conint(ge=1)] 
    
    
class LeverageModel(BaseModel):
    CRYPTOCURRENCIES: int 
    SHARES: int
    INDICES: int
    CURRENCIES: int
    COMMODITIES: int

class AccountPreferenceModel(BaseModel):
    hedging_mode: bool
    leverages: LeverageModel
    