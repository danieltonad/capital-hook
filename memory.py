from enums.trade import TradeDirection, TradeInstrument
from typing import Dict
class Memory:
    positions: dict = {}
    deal_ids: set = set()
    capital_auth_header: dict = {}
    epics: list = []
    instruments: dict = {}
    market_data: dict = {}
    preferences: dict = {}
    hooked_trades: Dict[str, TradeDirection] = {}
    
    def __init__(self):
        pass
        # self.positions = {}
        # self.deal_ids = set()
        # self.capital_auth_header = {}
        # self.epics = []
        # self.instruments = {}
        # self.market_data = {}
        # self.preferences = {}
        
        
    def update_position(self, deal_id: str, pnl: float, trade_direction: TradeDirection, epic: str, trade_size: float, hook_name: str):
        self.positions[deal_id] = {
            "epic": epic,
            "pnl": pnl,
            "trade_direction": trade_direction,
            "trade_size": trade_size,
            "hook_name": hook_name
            
        }
        
    def remove_position(self, deal_id: str):
        if deal_id in self.positions:
            del self.positions[deal_id]
    
    
    def update_deal_id(self, deal_id: str):
        self.deal_ids.add(deal_id)
    
    def remove_deal_id(self, deal_id: str):
        if deal_id in self.deal_ids:
            self.deal_ids.remove(deal_id)
            
    def update_capital_auth_header(self, header: dict):
        self.capital_auth_header = header
    
    def update_epics(self, epics: list, instruments: dict):
        self.epics = epics
        self.instruments = instruments
        
    def update_market_data(self, epic: str, ask: float, bid: float, timestamp: str):
        """Update market_data with the latest stream data for an epic."""
        self.market_data[epic] = {"ask": ask, "bid": bid, "timestamp": timestamp}
        
    def get_current_price(self, epic: str) -> tuple[float, float]:
        """Get the latest ask and bid price for a given epic."""
        if epic in self.market_data:
            return self.market_data[epic]["ask"], self.market_data[epic]["bid"]
        else:
            return None, None
    
    def get_leverage(self, epic: str) -> int:
        """Get the leverage for a given epic."""
        instrument = self.instruments.get(epic, "")
        return self.preferences.get("leverages", {}).get(instrument, {}).get("current", 1)
    
    def get_trade_instrument(self, epic: str) -> TradeInstrument:
        """Get the trade instrument for a given epic."""
        return TradeInstrument(self.instruments.get(epic, ""))
    
    def update_trading_view_hooked_trades(self, epic: str, direction: TradeDirection, hook_name: str):
        self.hooked_trades[f"{epic}_{hook_name}"] = direction
    
    def get_trading_view_hooked_trade_side(self, epic: str, hook_name) -> TradeDirection:
        return self.hooked_trades.get(f"{epic}_{hook_name}", TradeDirection.NEUTRAL)
        
        
    
    
    

memory = Memory()



# {'hedgingMode': True, 'leverages': {'SHARES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'CURRENCIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 30, 50, 100, 200]}, 'INDICES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}, 'CRYPTOCURRENCIES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'COMMODITIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}}}