from pydantic import BaseModel, conint, root_validator
from enums.trade import TradeDirection
from typing import Annotated
from typing import Literal
from memory import memory, TradeInstrument

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
    
    @root_validator
    def validate_all_fields(cls, values):
        for field, value in values.items():
            if not isinstance(value, int):
                raise ValueError(f"{field} must be an integer")
            if value <= 0:
                raise ValueError(f"{field} must be greater than 0")
        return values
    
    

class AccountPreferenceModel(BaseModel):
    hedging_mode: bool
    leverages: LeverageModel
    