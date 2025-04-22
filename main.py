from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.api import api
from routes.webhook import webhook
from database import settings, create_connection, migrate_db
from service.capital_socket import CapitalSocket

app = FastAPI(
    title=settings.APP_TITLE
)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    settings.DB_CONNECTION = await create_connection()
    await migrate_db()
    
    
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    # close DB connection
    if settings.DB_CONNECTION:
        await settings.DB_CONNECTION.close()
        settings.DB_CONNECTION = None
    
    # close HTTP session
    await settings.session.aclose()
    # capital socket initialization
    settings.capital_socket_service = CapitalSocket()


app.include_router(api, prefix="/api", tags=["API"])
app.include_router(webhook, prefix="/webhook", tags=["Webhook"])


app.mount("/assets", StaticFiles(directory="assets"), name="assets")