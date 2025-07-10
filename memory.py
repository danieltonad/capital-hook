from enums.trade import TradeDirection, TradeInstrument
from typing import Dict
from settings import settings, TradeMode


class Memory:
    positions: dict = {TradeMode.DEMO.value: {}, TradeMode.LIVE.value: {}}
    deal_ids: set = set()
    capital_auth_header: dict = {}
    epics: list = []
    trading_hours: dict = {}
    instruments: dict = {}
    market_data: dict = {}
    preferences: dict = {}
    hooked_trades: Dict[str, TradeDirection] = {}
    portfolio: dict = {}


    def get_trade_mode_for_deal_id(self, deal_id: str) -> TradeMode | None:
        for mode in [TradeMode.DEMO, TradeMode.LIVE]:
            if deal_id in self.positions[mode.value]:
                return mode.value
        return None
    
    def update_position(self, deal_id: str, pnl: float, trade_direction: TradeDirection, epic: str, trade_size: float, hook_name: str, entry_date: str, entry_price: float):
        """Update or add positions."""
        mode = settings.TRADE_MODE.value
        if not self.get_trade_mode_for_deal_id(deal_id):
            self.positions[mode][deal_id] = {
                "epic": epic,
                "pnl": pnl,
                "trade_direction": trade_direction.value,
                "trade_size": trade_size,
                "hook_name": hook_name,
                "exit_trade": False,
                "entry_date": entry_date,
                "entry_price": entry_price,
            }
        else:
            self.positions[self.get_trade_mode_for_deal_id(deal_id)][deal_id]["pnl"] = pnl
        
    def manual_close_position(self, deal_id: str):
        """Mark a position as closed manually by setting exit_trade to True."""
        if deal_id in self.positions[settings.TRADE_MODE.value]:
            self.positions[settings.TRADE_MODE.value][deal_id]["exit_trade"] = True

    def manual_trade_exit_signal(self, deal_id: str) -> bool:
        """Check if a trade exit signal is set for a given deal_id."""
        return self.positions[settings.TRADE_MODE.value].get(deal_id, {}).get("exit_trade", False)


    def remove_position(self, deal_id: str):
        """Remove a position from the positions dictionary."""
        if deal_id in self.positions[self.get_trade_mode_for_deal_id(deal_id)]:
            del self.positions[self.get_trade_mode_for_deal_id(deal_id)][deal_id]


    def update_deal_id(self, deal_id: str):
        """Add a deal_id to the set of deal_ids."""
        self.deal_ids.add(deal_id)
    
    def remove_deal_id(self, deal_id: str):
        """Remove a deal_id from the set of deal_ids."""
        if deal_id in self.deal_ids:
            self.deal_ids.remove(deal_id)
            
    def update_capital_auth_header(self, header: dict):
        """Update the authorization header for Capital API."""
        self.capital_auth_header = header
    
    def update_epics(self, epics: list, instruments: dict):
        """Update the list of epics and their corresponding instruments."""
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
        """Update or add a hooked trade for a specific epic and hook name."""
        self.hooked_trades[f"{epic}_{hook_name}"] = direction
    
    def remove_trading_view_hooked_trades(self, epic: str, hook_name: str):
        """Remove a hooked trade for a specific epic and hook name."""
        del self.hooked_trades[f"{epic}_{hook_name}"]
    
    def get_trading_view_hooked_trade_side(self, epic: str, hook_name) -> TradeDirection:
        return self.hooked_trades.get(f"{epic}_{hook_name}", TradeDirection.NEUTRAL)
    
        
        
    
    
    

memory = Memory()



# {'hedgingMode': True, 'leverages': {'SHARES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'CURRENCIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 30, 50, 100, 200]}, 'INDICES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}, 'CRYPTOCURRENCIES': {'current': 20, 'available': [1, 2, 3, 4, 5, 10, 20]}, 'COMMODITIES': {'current': 200, 'available': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]}}}