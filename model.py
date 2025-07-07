from pydantic import BaseModel, conint
from enums.trade import TradeDirection, ExitType, TradeMode
from typing import Annotated
from typing import Literal, List, Optional


class TradingViewWebhookModel(BaseModel):
    epic: str
    direction: TradeDirection
    amount: Annotated[int, conint(ge=5)] 
    hook_name: str
    profit: Annotated[int, conint(ge=5)] 
    loss: Annotated[int, conint(ge=5)] 
    exit_criteria: List[ExitType]
    

class HookPayloadModel(BaseModel):
    epic: str
    hook_name: str
    direction: TradeDirection
    trade_amount: Annotated[float, conint(gt=10)]
    stop_loss: Annotated[float, conint(gt=0)]
    take_profit: Annotated[float, conint(gt=0)]
    exit_criteria: List[ExitType]
    

class TradeModeModel(BaseModel):
    mode: TradeMode