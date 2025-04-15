import asyncio, json
from settings import settings


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
        
            return {'X-SECURITY-TOKEN': X_SECURITY_TOKEN, 'CST': CST}
        except Exception as e:
            await asyncio.sleep(100)
            return await new_auth_header()
            
    
@staticmethod
async def portfolio_balance():
    try:
        header = settings.CAPITAL_AUTH_HEADER
        response = await settings.SESSION.get(f"{settings.get_capital_host()}/api/v1/accounts", headers=header)
        if response.status_code == 200:
            data = response.json()
            return data["accounts"]
    except Exception as e:
        # await Logger.app_log(title="PORTFOLIO_ERR", message=str(e))
        return {}
