from pydantic import BaseModel, conint
from enums.trade import TradeDirection
from typing import Annotated


class TradingViewWebhookModel(BaseModel):
    epic: str
    direction: TradeDirection
    trade_amount: Annotated[int, conint(ge=5)] 
    hook_name: str
    profit: Annotated[int, conint(ge=1)] 
    loss: Annotated[int, conint(ge=1)] 