from pydantic import BaseModel, conint, model_validator, field_validator
from enums.trade import TradeDirection, ExitType
from typing import Annotated
from typing import Literal, List, Optional


class TradingViewWebhookModel(BaseModel):
    epic: str
    direction: TradeDirection
    amount: Annotated[int, conint(ge=5)] 
    hook_name: str
    profit: Annotated[int, conint(ge=1)] 
    loss: Annotated[int, conint(ge=1)] 
    exit_criteria: List[ExitType]
    

class HookPayloadModel(BaseModel):
    epic: str
    hook_name: str
    direction: TradeDirection
    trade_amount: Annotated[float, conint(gt=10)]
    stop_loss: Annotated[float, conint(gt=0)]
    take_profit: Annotated[float, conint(gt=0)]
    exit_criteria: List[ExitType]
    
    
class LeverageModel(BaseModel):
    CRYPTOCURRENCIES: Optional[int] = None
    SHARES: Optional[int] = None
    INDICES: Optional[int] = None
    CURRENCIES: Optional[int] = None
    COMMODITIES: Optional[int] = None

    @model_validator(mode="after")
    def check_at_least_one(self):
        if not any([
            self.CRYPTOCURRENCIES, self.SHARES,
            self.INDICES, self.CURRENCIES, self.COMMODITIES
        ]):
            raise ValueError('At least one leverage field must be provided')
        return self
    
    
class AccountPreferenceModel(BaseModel):
    hedging_mode: Optional[bool] = None
    leverages: Optional[LeverageModel] = None

    @model_validator(mode="after")
    def check_at_least_one(self):
        if self.hedging_mode is None and self.leverages is None:
            raise ValueError('At least one account preference field must be provided')
        return self
    