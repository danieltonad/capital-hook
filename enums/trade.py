from enum import Enum


class TradeDirection(Enum):
    SELL = "SELL"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    
    
class ExitType(Enum):
    TP = "TP"
    SL = "SL"
    USER = "USER"
    STRATEGY = "STRATEGY"
    EOD_CLOSE = "EOD_CLOSE"
    EOW_CLOSE = "EOW_CLOSE"
    RECALIBRATE = "RECALIBRATE"
    TRAILING_STOP = "TRAILING_STOP"
    
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