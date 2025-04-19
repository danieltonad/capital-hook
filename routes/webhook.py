from fastapi import APIRouter, BackgroundTasks, Request

webhook = APIRouter()

@webhook.post("/trading-view", tags=["TradingView Webhook Endpoint"])
async def tradingview_webhook_route(data, request: Request, background_task: BackgroundTasks):
    return "Wagwan!"