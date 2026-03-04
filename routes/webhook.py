from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from model import TradingViewWebhookModel, TradeDirection
from memory import memory, settings
from service.capital_api import is_market_closed
from logger import Logger

webhook = APIRouter()

@webhook.post("/trading-view")
async def tradingview_webhook_route(data: TradingViewWebhookModel, request: Request, background_task: BackgroundTasks):
    
    # validate whilested Tradingview IP Address
    client_ip = request.headers.get("x-forwarded-for", request.client.host)
    if str(client_ip) not in settings.TRADINGVIEW_IP_ADDRESS:
        await Logger.app_log(title="TradingView_Webhook_Error", message=f"IP {client_ip} not whitelisted")
        return JSONResponse(status_code=403, content={"message": "IP not whitelisted"})
    
    # validate capital.com epic
    if data.epic not in memory.epics:
        await Logger.app_log(title="TradingView_Webhook_Error", message=f"Epic {data.epic} not available")
        return JSONResponse(status_code=400, content={"message": "Invalid epic"})
    
    if data.direction in [TradeDirection.EXIT_BUY, TradeDirection.EXIT_SELL]:
        if memory.get_trading_view_hooked_trade_side(data.epic, data.hook_name, data.trade_mode).exit_direction() == data.direction:
            memory.update_trading_view_hooked_trades(epic=data.epic, direction=data.direction, hook_name=data.hook_name, trade_mode=data.trade_mode) # update exit trade
        await Logger.app_log(title="TradingView_Webhook", message=f"Exit webhook received for {data.epic} {data.direction.value} trade") 
        return JSONResponse(status_code=200, content={"message": "Exit trade executed"})
    
    # multiple position check - if the same trade is already executed and multi_position is false, do not execute the trade again
    if memory.get_trading_view_hooked_trade_side(data.epic, data.hook_name, data.trade_mode) == data.direction and not data.multi_position: 
        await Logger.app_log(title="TradingView_Webhook_Error", message=f"Trade already executed for {data.epic} {data.direction.value}")
        return JSONResponse(status_code=400, content={"message": "Trade already executed"})
    
    
    from hook_trade import HookedTradeExecution
    hooked_trade = HookedTradeExecution(epic=data.epic, trade_amount=data.amount, profit=data.profit, loss=data.loss, hook_name=data.hook_name, trade_direction=data.direction, exit_criteria=data.exit_criteria, trail_sl=data.trail_sl, trade_mode=data.trade_mode)
    background_task.add_task(hooked_trade.execute_trade)
    
    memory.update_trading_view_hooked_trades(epic=data.epic, direction=data.direction, hook_name=data.hook_name, trade_mode=data.trade_mode) # update the hooked trades
    await Logger.app_log(title="TradingView_Webhook", message=f"Webhook received from {client_ip} for {data.epic} {data.direction.value} trade")