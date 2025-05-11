from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from service.capital_api import set_account_preferences
from model import AccountPreferenceModel
from memory import memory

api = APIRouter()


@api.get("/history", tags=["Trade History"])
async def get_history(request: Request):
    """
    Get the history of trades.
    """
    pass


@api.get("/preference", tags=["Account Preference"])
async def get_preference(request: Request):
    """
    Get the account preference.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=memory.preferences
    )
    
    
@api.put("/preferences", tags=["Update Account Preference"])
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
    

@api.delete("/trade/{}", tags=["Manual CLoase Trade"])
async def manual_close_trade(request: Request, deal_id: str):
    pass