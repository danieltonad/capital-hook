from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from service.capital_api import set_account_preferences, portfolio_balance
from model import AccountPreferenceModel, memory


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
    
    
@api.put("/preferences")
async def update_preference(request: Request, data: AccountPreferenceModel):
    """
    Update the account preference.
    """
    data = await request.json()
    memory.preferences.update(data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.preferences
    )
    

@api.delete("/trade/{deal_id}")
async def manual_close_trade(request: Request, deal_id: str):
    pass