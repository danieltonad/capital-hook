from settings import settings
from memory import memory
from service.capital_api import update_auth_header, update_markets
import asyncio



async def play_book():
    await update_auth_header()
    
    await update_markets()
    epic = "US500" #memory.epics[347]
    instrument = memory.instruments[epic]
    print(epic, instrument)
    
    
    await settings.session.aclose()
    
    
    
    

asyncio.run(play_book())


# [
#     {
#         'instrumentName': 'FIS/USD', 
#         'instrumentId': 6919076349826244, 
#         'expiry': '-', 
#         'epic': 'FISUSD', 
#         'symbol': 'FIS/USD', 
#         'instrumentType': 'CRYPTOCURRENCIES', 
#         'marketStatus': 'TRADEABLE', 
#         'lotSize': 1, 
#         'high': 0.13087, 
#         'low': 0.12153, 
#         'percentageChange': 0.24, 
#         'netChange': -0.0028, 
#         'bid': 0.12365, 
#         'offer': 0.13, 
#         'updateTime': '2025-04-15T22:41:19.150', 
#         'updateTimeUTC': '2025-04-15T21:41:19.150', 
#         'delayTime': 0, 
#         'streamingPricesAvailable': True, 
#         'scalingFactor': 1, 
#         'marketModes': ['LONG_ONLY'], 
#         'pipPosition': 0, 'tickSize': 1e-05
#     }
# ]
    