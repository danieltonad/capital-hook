from fastapi import APIRouter, BackgroundTasks, Request

api = APIRouter()

@api.post("webhook/trading-view", tags=["TradingView Webhook Endpoint"])
async def tradingview_webhook_route(data, request: Request, background_task: BackgroundTasks):
    return "Wagwan!"