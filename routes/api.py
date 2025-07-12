from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from service.capital_api import portfolio_balance, memory
from model import HookPayloadModel, TradeModeModel, ExitType


api = APIRouter()


@api.get("/portfolio")
async def get_portfolio():
    """
    Get the portfolio overview.
    """
    portfolio = await portfolio_balance()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=portfolio
    )

@api.get("/positions")
async def get_portfolio():
    """
    Poll Positions
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.positions
    )

@api.get("/history")
async def get_history():
    """
    Get the history of trades.
    """
    pass


@api.get("/preference")
async def get_preference():
    """
    Get the account preference.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.preferences
    )
    
    

@api.delete("/trade/{deal_id}")
async def manual_close_trade(deal_id: str):
    memory.manual_close_position(deal_id)


@api.post("/mode")
async def update_trade_mode(data: TradeModeModel):
    from settings import settings
    await settings.update_trade_mode(data.mode)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Trade mode updated, [{settings.TRADE_MODE.value}]!"}
    )


@api.post("/generate-payload")
async def generate_payload(data: HookPayloadModel):
    """
    Generate tradingview webhook payload.
    """
    mapping = {
        'take_profit_exit': ExitType.TP.value,
        'stop_loss_exit': ExitType.SL.value,
        'strategy_exit': ExitType.STRATEGY.value,
        'market_close_exit': ExitType.MKT_CLOSED.value
    }

    payload = {
        "epic": "{{ticker}}",
        "direction": data.direction.value,
        "amount": data.trade_amount,
        "hook_name": data.hook_name.upper(),
        "profit": data.take_profit,
        "loss": data.stop_loss,
        "exit_criteria": [
        v for k, v in mapping.items() if getattr(data, k, None) == 'on'
    ]
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload
    )