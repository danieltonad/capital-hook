import asyncio
from enums.trade import TradeDirection, ExitType
from logger import Logger
from service.capital_api import open_trade, close_trade, is_market_closed
from datetime import datetime
from database import insert_trade_history
from enums.trade import TradeInstrument
from service.capital_socket import capital_socket, memory
from utils import round_trade_size
from typing import List

class HookedTradeExecution:
    trade_direction: TradeDirection
    epic: str
    trade_amount: int
    hook_name: str
    profit: int
    loss: int
    deal_id: str
    leverage: int
    entry_price: float
    exit_price: float
    trade_size: float
    trade_instrument: TradeInstrument
    exit_criteria: List[ExitType]
    stop_loss_price: float
    target_profit_price: float
    exit_type: ExitType
    opened_trade_at: datetime
    
    
    def __init__(self, trade_direction: TradeDirection, epic: str, trade_amount: int, profit: int, loss: int, hook_name: str, exit_criteria: List[ExitType]):
        self.trade_direction = trade_direction
        self.epic = epic
        self.trade_amount = trade_amount
        self.hook_name = hook_name
        self.profit = profit
        self.loss = loss
        self.deal_id = None
        self.exit_criteria = exit_criteria
        self.leverage = memory.get_leverage(epic)
        self.trade_instrument = memory.get_trade_instrument(epic)
        
    
    def __log_trade_position(self, profit_loss, percentage):
        print(f"[{self.epic}] [{self.trade_direction.value}] PnL: {profit_loss:.2f} -", f"{percentage:.2f}%   [{self.hook_name.upper()}]")
        
    async def log_trade(self, status: str) -> None:
        await Logger.app_log(title="TRADE_LOG", message=f"{self.epic} {status} {self.trade_direction.value} trade -> {self.trade_size}  [{self.hook_name.upper()}]")
        
    async def sleep_time(self) -> None:
        await asyncio.sleep(1.12)
            
    def __set_trade_size(self):
        self.capital_size = float(self.trade_amount)
        leverage_size = self.capital_size * memory.get_leverage(self.epic)
        self.trade_size = float(leverage_size / self.entry_price)
        if self.trade_instrument == TradeInstrument.CURRENCIES:
            self.trade_size = round(self.trade_size, -2)
        elif self.trade_instrument == TradeInstrument.SHARES:
            self.trade_size = round(self.trade_size)
        elif self.trade_instrument == TradeInstrument.COMMODITIES:
            self.trade_size = round(self.trade_size, 1)
        elif self.trade_instrument == TradeInstrument.INDICES:
            self.trade_size = TradeInstrument(self.trade_size) if self.trade_size > 2 else float(f"{self.trade_size:.2f}")
        else:
            self.trade_size = float(f"{self.trade_size:.2g}") if self.trade_size < 1 else round_trade_size(self.trade_size) if self.trade_size > 2 else float(f"{self.trade_size:.2f}")
        return leverage_size
            
    async def __risk_reward_setup(self):
        ask, bid =  memory.get_current_price(self.epic)
        self.entry_price = float(ask) if self.trade_direction == TradeDirection.BUY else float(bid)
        reward, risk =  self.profit, self.loss
        leverage_size = self.__set_trade_size()
        
        # Price movement for loss and profit
        loss_price_move = risk / self.trade_size
        profit_price_move = reward / self.trade_size
        
        # Set stop-loss and target-profit
        if self.trade_direction == TradeDirection.BUY:
            self.stop_loss_price = float(self.entry_price - loss_price_move)
            self.target_profit_price = float(self.entry_price + profit_price_move)
        elif self.trade_direction == TradeDirection.SELL:
            self.stop_loss_price = float(self.entry_price + loss_price_move)
            self.target_profit_price = float(self.entry_price - profit_price_move)
            
    def __calculate_profit_loss(self, current_price: float) -> tuple:
        if self.trade_direction == TradeDirection.BUY:
            profit_loss = float((current_price - self.entry_price) * self.trade_size)
            percentage = float(((current_price - self.entry_price) / self.entry_price) * 100)
        elif self.trade_direction == TradeDirection.SELL:
            profit_loss = float((self.entry_price - current_price) * self.trade_size)
            percentage = float(((self.entry_price - current_price) / self.entry_price) * 100)
            
        return profit_loss, percentage
        
    
    async def __monitor_position(self) -> tuple:
        ask, bid = memory.get_current_price(self.epic)
        current_price = bid if self.trade_direction == TradeDirection.BUY else ask
        profit_loss, percentage = self.__calculate_profit_loss(current_price)
        self.exit_price = ask if self.trade_direction == TradeDirection.BUY else bid
        memory.update_position(deal_id=self.deal_id, pnl=profit_loss, trade_direction=self.trade_direction, epic=self.epic, trade_size=self.trade_size, entry_date=self.opened_trade_at.strftime("%d %b %H:%M"), hook_name=self.hook_name)
        
        # reward monitor long
        if ExitType.TP in self.exit_criteria and current_price >= self.target_profit_price and self.trade_direction == TradeDirection.BUY:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
            self.exit_type = ExitType.TP
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # risk monitor long
        elif ExitType.SL in self.exit_criteria and current_price <= self.stop_loss_price and self.trade_direction == TradeDirection.BUY:
                await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
                self.exit_type = ExitType.SL
                await self.log_trade("closed")
                return True, profit_loss, percentage
            
        # reward monitor short
        elif ExitType.TP in self.exit_criteria and current_price <= self.target_profit_price and self.trade_direction == TradeDirection.SELL:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
            self.exit_type = ExitType.TP
            self.log_trade("closed")
            return True, profit_loss, percentage
        
        # risk monitor short
        elif ExitType.SL in self.exit_criteria and current_price >= self.stop_loss_price and self.trade_direction == TradeDirection.SELL:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
            self.exit_type = ExitType.SL
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # market closed?
        elif ExitType.MKT_CLOSED in self.exit_criteria and await is_market_closed(self.epic):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
            self.exit_type = ExitType.MKT_CLOSED
            await self.log_trade("closed")
            return True, profit_loss, percentage
            
        
        elif memory.manual_trade_exit_signal(self.deal_id):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id)
            self.exit_type = ExitType.USER
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        else:
            return False, profit_loss, percentage
        
        

    async def execute_trade(self):
        try:
            await capital_socket.subscribe_to_epic(self.epic)
            
            # set risk reward
            await self.__risk_reward_setup()
            
            # open position
            self.deal_id = await open_trade(epic=self.epic, size=self.trade_size, trade_direction=self.trade_direction)
            if not self.deal_id:
                raise Exception("Market Closed")
            await self.log_trade("opened")
            self.opened_trade_at = datetime.now()
                
            # monitor trade
            while True:
                status, profit_loss , percentage = await self.__monitor_position()
                # self.__log_trade_position(profit_loss, percentage)
                memory.update_position(deal_id=self.deal_id, pnl=profit_loss, trade_direction=self.trade_direction, epic=self.epic, trade_size=self.trade_size, entry_date=self.opened_trade_at.strftime("%d %b %H:%M"), hook_name=self.hook_name)
                
                if status:
                    await insert_trade_history(trade_id=self.deal_id, epic=self.epic, size=self.trade_size, pnl=profit_loss, pnl_percentage=percentage, direction=self.trade_direction.value, exit_type=self.exit_type.value, hook_name=self.hook_name.upper(), entry_price=self.entry_price, exit_price=self.exit_price, opened_at=self.opened_trade_at.strftime("%Y-%m-%d %H:%M:%S"), closed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    break
                
                await self.sleep_time()
            
            # remove position from memory
            memory.remove_position(self.deal_id)
            
            
        except Exception as err:
            await Logger.app_log(title=f"{self.hook_name.upper()}_ERR_[{self.epic}]", message=str(err))

