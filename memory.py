
class Memory:
    def __init__(self):
        self.positions: dict = {}
        self.deal_ids: set = set()
        self.capital_auth_header: dict = {}
        
        
    def update_position(self, key: str):
        pass
    
    
    def update_deal_id(self, deal_id: str):
        self.deal_ids.add(deal_id)
    
    def remove_deal_id(self, deal_id: str):
        if deal_id in self.deal_ids:
            self.deal_ids.remove(deal_id)
            
    def update_capital_auth_header(self, header: dict):
        self.capital_auth_header = header
    
    
    

memory = Memory()