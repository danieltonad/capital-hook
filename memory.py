
class Memory:
    def __init__(self):
        self.positions: dict = {}
        self.deal_ids: set = set()
        self.capital_auth_header: dict = {}
        epics: list = []
        instruments: dict = {}
        market_data: dict = {}
        
        
    def update_position(self, key: str):
        pass
    
    
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
    
    
    

memory = Memory()