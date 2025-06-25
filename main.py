from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.api import api
from routes.webhook import webhook
from routes.view import view
from database import settings, migrate_db
from service.capital_socket import CapitalSocket
from memory import memory
from service.capital_api import get_account_preferences, update_markets,update_auth_header
from job import jobs

app = FastAPI(
    title=settings.APP_TITLE
)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """# create DB connection
    await migrate_db() # migrate DB
    
    
    # update market data
    await update_auth_header()
    await update_markets()
    print(f"{len(memory.epics):,} market data updated")
    
    # prefetch perference data
    preferences = await get_account_preferences()
    memory.preferences = preferences
    
    # initialize jobs
    await jobs.run()
    
    
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


app.include_router(view, tags=["View"])
app.include_router(api, prefix="/api", tags=["API"])
app.include_router(webhook, prefix="/webhook", tags=["Webhook"])


app.mount("/assets", StaticFiles(directory="assets"), name="assets")