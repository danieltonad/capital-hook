from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates, _TemplateResponse
from memory import memory
from utils import pnl_display, entry_price_display
from database import get_trade_history
from settings import settings


view = APIRouter()
templates = Jinja2Templates(directory="views")



@view.get("/", tags=["Dashboard"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    from service.capital_api import portfolio_balance
    data = await portfolio_balance()
    portfolio = data.get("balance", {})
    symbol = data.get("symbol", "#")
    positions = []
    
    for position in memory.positions.keys():
        leverage = memory.get_leverage(memory.positions[position].get("epic", ""))
        leverage = f"{leverage}:1"
        positions.append({
            "deal_id": position,
            "epic": memory.positions[position].get("epic", "N/A"),
            "entry_price": entry_price_display(memory.positions[position].get("entry_price", 0.0)),
            "pnl": pnl_display(symbol=symbol, pnl=memory.positions[position].get('pnl', 0)),
            "direction": memory.positions[position].get("trade_direction", "N/A"),
            "size": memory.positions[position].get("trade_size", 0),
            "hook_name": memory.positions[position].get("hook_name", "N/A"),
            "date": memory.positions[position].get("entry_date", "N/A"),
        })

    data = {
        "positions": positions,
        "portfolio": {
            "balance": f"{symbol}{portfolio.get('balance', 0):,}",
            "deposit": f"{symbol}{portfolio.get('deposit', 0):,}",
            "available": f"{symbol}{portfolio.get('available', 0):,}",
            "pnl": f"{symbol}{portfolio.get('profitLoss', 0):,}",

        }
    }
    return templates.TemplateResponse("pages/index.html", {"request": request, "data": data, "mode": settings.TRADE_MODE.value,})

@view.get("/positions", tags=["Positions"])
async def position_view(request: Request) -> _TemplateResponse:
    positions = []
    
    for position in memory.positions.keys():
        leverage = memory.get_leverage(memory.positions[position].get("epic", ""))
        leverage = f"{leverage}:1"
        symbol = memory.portfolio.get("symbol", "#")
        positions.append({
            "deal_id": position,
            "epic": memory.positions[position].get("epic", "N/A"),
            "entry_price": entry_price_display(memory.positions[position].get("entry_price", 0.0)),
            "pnl": pnl_display(symbol=symbol, pnl=memory.positions[position].get('pnl', 0)),
            "direction": memory.positions[position].get("trade_direction", "N/A"),
            "size": memory.positions[position].get("trade_size", 0),
            "hook_name": memory.positions[position].get("hook_name", "N/A"),
            "date": memory.positions[position].get("entry_date", "N/A"),
        })

    data = {
        "positions": positions
    }
    return templates.TemplateResponse("components/positions.html", {"request": request, "data": data})


@view.get("/portfolio", tags=["Positions"])
async def portfolio_view(request: Request) -> _TemplateResponse:
    from service.capital_api import portfolio_balance
    data = await portfolio_balance()
    portfolio = data.get("balance", {})
    symbol = data.get("symbol", "#")
    data = {
        "portfolio": {
            "balance": f"{symbol}{portfolio.get('balance', 0):,}",
            "deposit": f"{symbol}{portfolio.get('deposit', 0):,}",
            "available": f"{symbol}{portfolio.get('available', 0):,}",
            "pnl": pnl_display(symbol=symbol, pnl=portfolio.get('profitLoss', 0)),
        },
        "mode": settings.TRADE_MODE.value,
    }
    return templates.TemplateResponse("components/portfolio.html", {"request": request, "data": data})


@view.get("/history", tags=["Trade History"])
async def trade_history_view(request: Request) -> _TemplateResponse:
    data = await get_trade_history()
    trades = data.get("trades", [])
    profits = data.get("profits", "0.00")
    loasses = data.get("loasses", "0.00")
    spreads = data.get("spreads", "0.00")
    pnl = data.get("pnl", "0.00")
    count = data.get("count", "0.00")
    return templates.TemplateResponse("pages/history.html", {
        "request": request, 
        "trades": trades, 
        "profits": profits, 
        "loasses": loasses, 
        "spreads": spreads, 
        "pnl": pnl, 
        "count": count,
        "mode": settings.TRADE_MODE.value,
    })




@view.get("/config", tags=["Config"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    data = {
        "positions": {}
    }
    return templates.TemplateResponse("pages/config.html", {"request": request, "data": data, "mode": settings.TRADE_MODE.value})