from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates, _TemplateResponse


view = APIRouter()
templates = Jinja2Templates(directory="views")



@view.get("/", tags=["Dashboard"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    data = {
        "positions": {}
    }
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
