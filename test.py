from settings import settings
from memory import memory
from service.capital_api import update_auth_header, get_all_epics
import asyncio



async def play_book():
    await update_auth_header()
    print(memory.capital_auth_header)
    
    epics = await get_all_epics()
    print(len(epics))
    
    

asyncio.run(play_book())