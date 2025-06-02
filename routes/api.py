from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from service.capital_api import set_account_preferences, portfolio_balance, memory
from model import AccountPreferenceModel


api = APIRouter()


@api.get("/portfolio")
async def get_portfolio(request: Request):
    """
    Get the portfolio overview.
    """
    portfolio = await portfolio_balance()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=portfolio
    )

@api.get("/positions")
async def get_portfolio(request: Request):
    """
    Poll Positions
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.positions
    )

@api.get("/history")
async def get_history(request: Request):
    """
    Get the history of trades.
    """
    pass


@api.get("/preference")
async def get_preference(request: Request):
    """
    Get the account preference.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.preferences
    )
    
    
# @api.put("/preferences")
# async def update_preference(request: Request, data: AccountPreferenceModel):
#     """
#     Update the account preference.
#     """
#     data = await request.json()
#     memory.preferences.update(data)
#     # await set_account_preferences(hedging_mode=data.hedging_mode, leverages=data.leverages)
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content=memory.preferences
    # )
    

@api.delete("/trade/{deal_id}")
async def manual_close_trade(request: Request, deal_id: str):
    memory.manual_close_position(deal_id)
    
    
@api.post("/generate-payload")
async def generate_payload(request: Request):
    """
    Generate a payload for a trade.
    """
    data = await request.json()
    payload = {
        "epic": data.get("epic"),
        "trade_size": data.get("trade_size"),
        "direction": data.get("direction"),
        "stop_loss": data.get("stop_loss"),
        "take_profit": data.get("take_profit")
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload
    )