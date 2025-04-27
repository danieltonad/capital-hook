from enum import Enum


class TradeDirection(Enum):
    SELL = "SELL"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    
    
class ExitType(Enum):
    TP = "TP"
    SL = "SL"
    USER = "USER"
    MKT_CLOSED = "MKT_CLOSED"
    
class TradeMode(Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"

class TradeInstrument(Enum):
    CRYPTOCURRENCIES = "CRYPTOCURRENCIES"
    SHARES = "SHARES"
    INDICES = "INDICES"
    CURRENCIES = "CURRENCIES"
    COMMODITIES = "COMMODITIES"
    UNKONWN = ""