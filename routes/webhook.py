from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from model import TradingViewWebhookModel
from settings import settings
from memory import memory
from logger import Logger
from hook_trade import HookedTradeExecution

webhook = APIRouter()

@webhook.post("/trading-view", tags=["TradingView Webhook Endpoint"])
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
    
    hooked_trade = HookedTradeExecution(epic=data.epic, trade_amount=data.amount, profit=data.profit, loss=data.loss, hook_name=data.hook_name)
    background_task.add_task(hooked_trade.execute)