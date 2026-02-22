from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.api import api
from routes.webhook import webhook
from routes.view import view
from memory import memory, settings, TradeMode
from service.capital_api import get_account_preferences, update_markets,update_auth_header
from job import jobs

app = FastAPI(
    title=settings.APP_TITLE
)

@app.on_event("startup")
async def startup_event():
    from database import migrate_db
    """
    Startup event handler
    """
    await migrate_db() # migrate DB
    await settings.sync_trade_mode()
    
    
    # update market data
    await update_auth_header(TradeMode.DEMO)
    await update_auth_header(TradeMode.LIVE)
    await update_markets()
    print(f"{len(memory.epics):,} market data updated")
    
    # prefetch perference data
    for trade_mode in [TradeMode.DEMO, TradeMode.LIVE]:
        preferences = await get_account_preferences(trade_mode)
        if preferences:
            print(f"Preferences for {trade_mode.value} fetched and updated in memory.")
            memory.update_preferences(preferences, trade_mode)
    
    # initialize jobs
    await jobs.run()

    # resume trades
    await jobs.resume_trades()
    
    
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