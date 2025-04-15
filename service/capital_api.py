import asyncio, json
from settings import settings
from enums.trade import TradeDirection
from memory import memory


async def new_auth_header() -> dict:
        try:
            payload = json.dumps({
            "identifier": settings.CAPITAL_IDENTITY,
            "password": settings.CAPITAL_PASSWORD,
            "encryptedPassword": False
            })
            headers = {
                'X-CAP-API-KEY': settings.CAPITAL_API_KEY,
                'Content-Type': 'application/json'
            }
            response = await settings.session.post(f"{settings.get_capital_host()}/api/v1/session", headers=headers, data=payload)
            # print(response.status_code ,response.json())
            header: dict = response.headers
            CST = header.get("CST")
            X_SECURITY_TOKEN = header.get("X-SECURITY-TOKEN")
            # print(CST, X_SECURITY_TOKEN)
            memory.update_capital_auth_header({'X-SECURITY-TOKEN': X_SECURITY_TOKEN, 'CST': CST})
            
        except Exception as e:
            await asyncio.sleep(100)
            return await new_auth_header()
        
async def get_epic_deal_id(self, epic: str, size: float, trade_direction: TradeDirection) -> str:
    try:
        open_positions = await self.get_open_positions()
        for position in open_positions:
            if position["epic"] == epic and float(position["size"]) == size and position["direction"] == trade_direction.value and position["deal_id"] not in memory.deal_ids:
                return position["deal_id"]
        return None
    except Exception as e:
        # await Logger.app_log(title="DEAL_ID_ERR", message=str(e))
        pass
            
    

async def portfolio_balance():
    try:
        header = memory.capital_auth_header
        response = await settings.SESSION.get(f"{settings.get_capital_host()}/api/v1/accounts", headers=header)
        if response.status_code == 200:
            data = response.json()
            return data["accounts"]
    except Exception as e:
        # await Logger.app_log(title="PORTFOLIO_ERR", message=str(e))
        return {}
