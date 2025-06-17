from enums.trade import TradeDirection, TradeInstrument
from typing import Dict


class Memory:
    positions: dict = {}
    deal_ids: set = set()
    capital_auth_header: dict = {}
    epics: list = []
    trading_hours: dict = {}
    instruments: dict = {}
    market_data: dict = {}
    preferences: dict = {}
    hooked_trades: Dict[str, TradeDirection] = {}
    console_data: dict = {"msg": []}
    portfolio: dict = {}

        
    def update_console_data_msg(self, msg: str):
        """Update the console data message."""
        self.console_data["msg"].append(msg)
        if len(self.console_data["msg"]) > 5:
            self.console_data["msg"].pop(0)
    
    def update_position(self, deal_id: str, pnl: float, trade_direction: TradeDirection, epic: str, trade_size: float, hook_name: str, entry_date: str):
        if self.positions.get(deal_id, None):
            self.positions[deal_id]["pnl"] = f"{pnl:,.2f}"
            self.positions[deal_id]["trade_direction"] = trade_direction.value
            self.positions[deal_id]["epic"] = epic
            self.positions[deal_id]["trade_size"] = trade_size
            self.positions[deal_id]["hook_name"] = hook_name
            self.positions[deal_id]["entry_date"] = entry_date
            pass
        else:
            self.positions[deal_id] = {
                "epic": epic,
                "pnl": f"{pnl:,.2f}",
                # "trade_direction": trade_direction.value,
                # "trade_size": trade_size,
                # "hook_name": hook_name,
                "exit_trade": False,
                # "entry_date": entry_date,
            }
        
    def manual_close_position(self, deal_id: str):
        if deal_id in self.positions:
            self.positions[deal_id]["exit_trade"] = True
    
    def manual_trade_exit_signal(self, deal_id: str) -> bool:
        """Check if a trade exit signal is set for a given deal_id."""
        return self.positions.get(deal_id, {}).get("exit_trade", False)
        
        
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
    
    def get_leverage_available(self, instrument: TradeInstrument) -> list:
        """Get the available leverage for a given instrument."""
        return self.preferences.get("leverages", {}).get(instrument.value, {}).get("available", [1])
    
    def get_trade_instrument(self, epic: str) -> TradeInstrument:
        """Get the trade instrument for a given epic."""
        return TradeInstrument(self.instruments.get(epic, ""))
    
    def update_trading_view_hooked_trades(self, epic: str, direction: TradeDirection, hook_name: str):
        self.hooked_trades[f"{epic}_{hook_name}"] = direction
    
    def get_trading_view_hooked_trade_side(self, epic: str, hook_name) -> TradeDirection:
        return self.hooked_trades.get(f"{epic}_{hook_name}", TradeDirection.NEUTRAL)
    
        
        
    
    
    

memory = Memory()



# {'hedgingMode': True, 'leverages': {'SHARES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'CURRENCIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 30, 50, 100, 200]}, 'INDICES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}, 'CRYPTOCURRENCIES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'COMMODITIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}}}