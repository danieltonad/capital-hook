from enum import Enum


class TradeDirection(Enum):
    SELL = "SELL"
    BUY = "BUY"
    
    
class ExitType(Enum):
    TP = "TP"
    SL = "SL"
    USER = "USER"
    
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