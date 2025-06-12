from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates, _TemplateResponse


view = APIRouter()
templates = Jinja2Templates(directory="views")



@view.get("/", tags=["Dashboard"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    from service.capital_api import portfolio_balance
    data = await portfolio_balance()
    portfolio = data.get("balance", {})
    symbol = data.get("symbol", "#")
    data = {
        "positions": {},
        "portfolio": {
            "balance": f"{symbol}{portfolio.get('balance', 0):,}",
            "deposit": f"{symbol}{portfolio.get('deposit', 0):,}",
            "available": f"{symbol}{portfolio.get('available', 0):,}",
            "pnl": f"{symbol}{portfolio.get('profitLoss', 0):,}",

        }
    }
    print(f"Portfolio: {data['portfolio']}")
    return templates.TemplateResponse("pages/index.html", {"request": request, "data": data})

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
