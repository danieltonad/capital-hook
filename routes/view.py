from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates, _TemplateResponse
from memory import memory


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
            "leverage": leverage,
            "pnl": f"{symbol}{memory.positions[position].get('pnl', 0):,}",
            "direction": memory.positions[position].get("trade_direction", "N/A"),
            "size": memory.positions[position].get("trade_size", 0),
            "hook_name": memory.positions[position].get("hook_name", "N/A"),
            "date": memory.positions[position].get("entry_date", "N/A"),
        })

    # dummy
    # positions.append({
    #     "deal_id": "position",
    #     "epic": "N/A",
    #     "leverage": "200:1",
    #     "pnl": -12.3,
    #     "direction": "BUY",
    #     "size": 1.23,
    #     "hook_name": "10/20 EMA",
    #     "date":"19 May 13:11",
    # })

    data = {
        "positions": positions,
        "portfolio": {
            "balance": f"{symbol}{portfolio.get('balance', 0):,}",
            "deposit": f"{symbol}{portfolio.get('deposit', 0):,}",
            "available": f"{symbol}{portfolio.get('available', 0):,}",
            "pnl": f"{symbol}{portfolio.get('profitLoss', 0):,}",

        }
    }
    print(data["positions"])
    return templates.TemplateResponse("pages/index.html", {"request": request, "data": data})

@view.get("/positions", tags=["Positions"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    positions = []
    
    for position in memory.positions.keys():
        leverage = memory.get_leverage(memory.positions[position].get("epic", ""))
        leverage = f"{leverage}:1"
        symbol = memory.portfolio.get("symbol", "#")
        positions.append({
            "deal_id": position,
            "epic": memory.positions[position].get("epic", "N/A"),
            "leverage": leverage,
            "pnl": f"{symbol}{memory.positions[position].get('pnl', 0)}",
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
async def dashboard_view(request: Request) -> _TemplateResponse:
    from service.capital_api import portfolio_balance
    data = await portfolio_balance()
    portfolio = data.get("balance", {})
    symbol = data.get("symbol", "#")
    data = {
        "portfolio": {
            "balance": f"{symbol}{portfolio.get('balance', 0):,}",
            "deposit": f"{symbol}{portfolio.get('deposit', 0):,}",
            "available": f"{symbol}{portfolio.get('available', 0):,}",
            "pnl": f"{symbol}{portfolio.get('profitLoss', 0):,}",
        }
    }
    return templates.TemplateResponse("components/portfolio.html", {"request": request, "data": data})



@view.get("/config", tags=["Config"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    data = {
        "positions": {}
    }
    return templates.TemplateResponse("pages/config.html", {"request": request, "data": data})

@view.get("/history", tags=["Trade History"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    data = {
        "positions": {}
    }
    return templates.TemplateResponse("pages/history.html", {"request": request, "data": data})
