from enum import Enum


class TradeDirection(Enum):
    SELL = "SELL"
    BUY = "BUY"
    
    
class ExitType(Enum):
    TP = "TP"
    SL = "SL"
    USER = "USER"

