import asyncio
from enums.trade import TradeDirection, ExitType
from logger import Logger
from service.capital_api import is_market_eow_close, close_trade, is_market_eod_close
from datetime import datetime
from database import save_trade_history
from enums.trade import TradeMode
from service.socket_manager import socket_manager, memory
from typing import List
from trail import TrailingSL

class ResumeTradeExecution:
    trade_direction: TradeDirection
    epic: str
    hook_name: str
    deal_id: str
    entry_price: float
    exit_price: float
    trade_size: float
    exit_criteria: List[ExitType]
    stop_loss_price: float
    target_profit_price: float
    exit_type: ExitType
    opened_trade_at: datetime
    position_mode: TradeMode
    profit_loss: float
    percentage: float
    trailing_stop: TrailingSL


    def __init__(self, epic: str, size: float, deal_id: str, entry_price: float, entry_date: str, trade_direction: TradeDirection, profit_price: int, loss_price: int, hook_name: str, exit_criteria: List[ExitType], trail_sl: int):
        from settings import settings
        self.trade_direction = trade_direction
        self.epic = epic
        self.trade_size = size
        self.hook_name = hook_name
        self.entry_price = entry_price
        self.target_profit_price = profit_price
        self.stop_loss_price = loss_price
        self.deal_id = deal_id
        self.exit_criteria = exit_criteria
        self.opened_trade_at = datetime.strptime(entry_date, "%d %b %H:%M")
        self.position_mode = settings.TRADE_MODE
        profit = abs(profit_price - entry_price) * size
        loss = abs(entry_price - loss_price) * size
        self.trailing_stop = TrailingSL(pnl=0.0, tp=profit, sl=loss, trail_range=trail_sl)
        
    
    def __log_trade_position(self, profit_loss, percentage):
        print(f"[{self.epic}] [{self.trade_direction.value}] PnL: {profit_loss:.2f} -", f"{percentage:.2f}%   [{self.hook_name.upper()}]")
        
    async def log_trade(self, status: str) -> None:
        await Logger.app_log(title="TRADE_LOG", message=f"{self.epic} {status} {self.trade_direction.value} trade -> {self.trade_size}  [{self.hook_name.upper()}]")
        
    async def sleep_time(self) -> None:
        await asyncio.sleep(1.12)
            
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
        if not current_price:
            return False, self.profit_loss, self.percentage
        
        profit_loss, percentage = self.__calculate_profit_loss(current_price)
        self.exit_price = ask if self.trade_direction == TradeDirection.BUY else bid
        memory.update_position(deal_id=self.deal_id, pnl=profit_loss, trade_direction=self.trade_direction, epic=self.epic, trade_size=self.trade_size, entry_date=self.opened_trade_at.strftime("%d %b %H:%M"), hook_name=self.hook_name, entry_price=self.entry_price)

        
        # reward monitor long
        if ExitType.TP in self.exit_criteria and current_price >= self.target_profit_price and self.trade_direction == TradeDirection.BUY:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.TP
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # risk monitor long
        elif ExitType.SL in self.exit_criteria and current_price <= self.stop_loss_price and self.trade_direction == TradeDirection.BUY:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.SL
            await self.log_trade("closed")
            return True, profit_loss, percentage
            
        # reward monitor short
        elif ExitType.TP in self.exit_criteria and current_price <= self.target_profit_price and self.trade_direction == TradeDirection.SELL:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.TP
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # risk monitor short
        elif ExitType.SL in self.exit_criteria and current_price >= self.stop_loss_price and self.trade_direction == TradeDirection.SELL:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.SL
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # market closed?
        elif ExitType.EOD_CLOSE in self.exit_criteria and await is_market_eod_close(self.epic):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.EOD_CLOSE
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # End Of Week market closed?
        elif ExitType.EOW_CLOSE in self.exit_criteria and await is_market_eow_close(self.epic):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.EOW_CLOSE
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # strategy switch
        elif ExitType.STRATEGY in self.exit_criteria and memory.get_trading_view_hooked_trade_side(self.epic, self.hook_name) != self.trade_direction:
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.STRATEGY
            await self.log_trade("closed")
            return True, profit_loss, percentage

        # reclibrate
        elif ExitType.RECALIBRATE in self.exit_criteria and memory.recalibrate_trade():
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.RECALIBRATE
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # trail stop
        elif self.trailing_stop.update_pnl(profit_loss):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.TRAIL
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        # manual exit
        elif memory.manual_trade_exit_signal(self.deal_id):
            await close_trade(epic=self.epic, size=self.trade_size, deal_id=self.deal_id, position_mode=self.position_mode)
            self.exit_type = ExitType.USER
            await self.log_trade("closed")
            return True, profit_loss, percentage
        
        
        else:
            self.profit_loss = profit_loss
            self.percentage = percentage
            return False, profit_loss, percentage
        
        

    async def execute_trade(self):
        try:
            await socket_manager.subscribe(self.epic)
                
            # monitor trade
            while True:
                status, profit_loss, percentage = await self.__monitor_position()
                
                if status:
                    await save_trade_history(trade_id=self.deal_id, epic=self.epic, size=self.trade_size, pnl=profit_loss, pnl_percentage=percentage, direction=self.trade_direction.value, exit_type=self.exit_type.value, hook_name=self.hook_name.upper(), entry_price=self.entry_price, exit_price=self.exit_price, opened_at=self.opened_trade_at.strftime("%Y-%m-%d %H:%M:%S"), closed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mode=self.position_mode)
                    break
                
                await self.sleep_time()
            
            # remove position from memory
            memory.remove_position(self.deal_id)

            # remove from hook trades when exits not on strategy
            if self.exit_type != ExitType.STRATEGY:
                memory.remove_trading_view_hooked_trades(self.epic, self.hook_name)

        except Exception as err:
            memory.remove_trading_view_hooked_trades(self.epic, self.hook_name)
            await Logger.app_log(title=f"{self.hook_name.upper()}_ERR_[{self.epic}]", message=str(err))


