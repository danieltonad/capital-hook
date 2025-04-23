
class Memory:
    positions: dict = {}
    deal_ids: set = set()
    capital_auth_header: dict = {}
    epics: list = []
    instruments: dict = {}
    market_data: dict = {}
    preferences: dict = {}
    
    def __init__(self):
        pass
        # self.positions = {}
        # self.deal_ids = set()
        # self.capital_auth_header = {}
        # self.epics = []
        # self.instruments = {}
        # self.market_data = {}
        # self.preferences = {}
        
        
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
        
    def get_current_price(self, epic: str) -> tuple[float, float]:
        """Get the latest ask and bid price for a given epic."""
        if epic in self.market_data:
            return self.market_data[epic]["ask"], self.market_data[epic]["bid"]
        else:
            return None, None
    
    def get_leverage(self, epic: str) -> int:
        """Get the leverage for a given epic."""
        instrument = self.instruments.get(epic, None)
        # if instrument:
        #     return self.
    
    
    

memory = Memory()