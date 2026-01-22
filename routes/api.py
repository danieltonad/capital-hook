from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from service.capital_api import portfolio_balance, memory
from model import HookPayloadModel, TradeModeModel, ExitType
from fastapi.responses import StreamingResponse


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

@api.get("/history/download")
async def download_history():
    """
    Download the history of trades.
    """
    from database import get_trade_history
    import csv
    import io
    data = await get_trade_history()
    trades = data.get("trades", [])
    if not trades:
        return StreamingResponse(io.StringIO("No trades found"), media_type="text/csv")

    # Remove 'id' from each trade
    filtered_trades = [{k: v for k, v in trade.items() if k != "id"} for trade in trades]

    # Write CSV to memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=filtered_trades[0].keys())
    writer.writeheader()
    writer.writerows(filtered_trades)
    output.seek(0)

    # Return as downloadable file
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trades.csv"}
    )



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
        'end_of_day_close_exit': ExitType.EOD_CLOSE.value,
        'end_of_week_close_exit': ExitType.EOW_CLOSE.value
    }

    payload = {
        "epic": "{{ticker}}",
        "direction": data.direction.value,
        "amount": data.trade_amount,
        "hook_name": data.hook_name.upper(),
        "profit": data.take_profit,
        "loss": data.stop_loss,
        "trail_sl": data.trail_sl,
        "exit_criteria": [
        v for k, v in mapping.items() if getattr(data, k, None) == 'on'
    ]
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload
    )




@api.get("/recalibrate/status")
async def get_recalibration_status():   
    """
    Get the recalibration status.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.recalibration_status()
    )