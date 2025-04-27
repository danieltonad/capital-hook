from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from model import TradingViewWebhookModel
from settings import settings
from memory import memory
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
    
    # 
    if memory.get_trading_view_hooked_trade_side(data.epic, data.hook_name) == data.direction: # check if the trade is already executed on trade side
        await Logger.app_log(title="TradingView_Webhook_Error", message=f"Trade already executed for {data.epic} {data.direction.value}")
    else:
        from hook_trade import HookedTradeExecution
        hooked_trade = HookedTradeExecution(epic=data.epic, trade_amount=data.amount, profit=data.profit, loss=data.loss, hook_name=data.hook_name, trade_direction=data.direction)
        background_task.add_task(hooked_trade.execute_trade)
        
        memory.update_trading_view_hooked_trades(epic=data.epic, direction=data.direction, hook_name=data.hook_name) # update the hooked trades in settings
        await Logger.app_log(title="TradingView_Webhook", message=f"Webhook received from {client_ip} for {data.epic} {data.direction.value} trade")