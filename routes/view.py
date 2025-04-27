from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates, _TemplateResponse


view = APIRouter()
templates = Jinja2Templates(directory="views")



@view.get("/", tags=["Dashboard"])
async def dashboard_view(request: Request) -> _TemplateResponse:
    """
    Dashboard view
    """
    data = {
        "positions": {}
    }
    return templates.TemplateResponse("pages/index.html", {"request": request, "data": data})
