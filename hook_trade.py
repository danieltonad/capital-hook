from enums.trade import TradeDirection
import asyncio

class HookedTradeExecution:
    trade_direction: TradeDirection
    epic: str
    trade_amount: int
    hook_name: str
    profit: int
    loss: int
    deal_id: str
    
    
    def __init__(self, trade_direction: TradeDirection, epic: str, trade_amount: int, profit: int, loss: int, hook_name: str):
        self.trade_direction = trade_direction
        self.epic = epic
        self.trade_amount = trade_amount
        self.hook_name = hook_name
        self.profit = profit
        self.loss = loss
        self.deal_id = None
        
        

    async def execute_trade(self):
        pass

