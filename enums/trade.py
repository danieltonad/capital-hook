from enum import Enum


class TradeDirection(Enum):
    SELL = "SELL"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    EXIT_BUY = "EXIT_BUY"
    EXIT_SELL = "EXIT_SELL"
    
    
class ExitType(Enum):
    TP = "TP"
    SL = "SL"
    USER = "USER"
    EXIT = "EXIT"
    STRATEGY = "STRATEGY"
    EOD_CLOSE = "EOD_CLOSE"
    EOW_CLOSE = "EOW_CLOSE"
    RECALIBRATE = "RECALIBRATE"
    TRAIL = "TRAIL"
    
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