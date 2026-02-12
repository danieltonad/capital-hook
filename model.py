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
    trail_sl: Optional[Annotated[int, conint(ge=5)]] = None
    exit_criteria: List[ExitType]
    trade_mode: TradeMode



class HookPayloadModel(BaseModel):
    hook_name: str
    direction: TradeDirection
    trade_amount: Annotated[float, conint(gt=10)]
    stop_loss: Annotated[float, conint(gt=10)]
    take_profit: Annotated[float, conint(gt=10)]
    trail_sl: Optional[Annotated[int, conint(gt=0)]] = None
    take_profit_exit: Optional[Literal['on']] = None
    stop_loss_exit: Optional[Literal['on']] = None
    strategy_exit: Optional[Literal['on']] = None
    end_of_day_close_exit: Optional[Literal['on']] = None
    end_of_week_close_exit: Optional[Literal['on']] = None


class TradeModeModel(BaseModel):
    mode: TradeMode



class PositionsModel(BaseModel):
    id: str
    epic: str
    size: float
    hook_name: str
    direction: TradeDirection
    entry_price: float
    entry_date: str
    exit_criteria: List[ExitType]
    profit_price: float
    loss_price: float
    trail_sl: int
    mode: TradeMode