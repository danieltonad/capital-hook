from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from service.capital_api import set_account_preferences, portfolio_balance, memory
from model import AccountPreferenceModel, HookPayloadModel


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
    
    

@api.delete("/trade/{deal_id}")
async def manual_close_trade(request: Request, deal_id: str):
    memory.manual_close_position(deal_id)
    
    
@api.post("/generate-payload")
async def generate_payload(data: HookPayloadModel):
    """
    Generate a payload for a trade.
    """
    
    payload = ""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload
    )