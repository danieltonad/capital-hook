import asyncio, json
from enums.trade import TradeDirection, TradeMode
from memory import memory, settings
from logger import Logger
from datetime import datetime, timedelta

async def update_auth_header() -> None:
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
        await Logger.app_log(title="UPDATE_AUTH_HEADER_ERR", message=str(e))
        await asyncio.sleep(100)
        return await update_auth_header()
        
        
async def get_epic_deal_id(epic: str, size: float, trade_direction: TradeDirection, retry: int = 0) -> str:
    try:
        open_positions = await get_open_positions()
        for position in open_positions:
            if position["epic"] == epic and float(position["size"]) == float(size) and position["direction"] == trade_direction.value and position["deal_id"] not in memory.deal_ids:
                return position["deal_id"]
            
        if retry < 5:
            retry += 1
            await asyncio.sleep(1)
            return await get_epic_deal_id(epic, size, trade_direction, retry)

        return None
    except Exception as e:
        await Logger.app_log(title="DEAL_ID_ERR", message=str(e))
        pass
    
    
async def get_open_positions() -> list:
    try:
        response = await settings.session.get(
            f"{settings.get_capital_host()}/api/v1/positions",
            headers = memory.capital_auth_header 
        )
        if response.status_code == 200:
            data = response.json()
            positions = data.get("positions", [])
            open_positions = [
                {
                    "epic": pos["market"]["epic"],
                    "size": float(pos["position"]["size"]),
                    "direction": pos["position"]["direction"],
                    "pnl": float(pos["position"]["upl"]),
                    "open_price": float(pos["position"]["level"]),
                    "deal_id": pos["position"]["dealId"],
                    "created_date": pos["position"]["createdDateUTC"]
                }
                for pos in positions
            ]
            return open_positions
        else:
            await Logger.app_log(
                title="FETCH_POSITIONS_FAIL",
                message=f"Status {response.status_code}: {response.text}"
            )
            return []
    except Exception as e:
        await Logger.app_log(title="FETCH_POSITIONS_ERR", message=str(e))
        return []
    
    
async def get_last_api_ask_bid(epic: str) -> tuple[float, float]:
        """Fetch the latest ask and bid price from REST API using httpx."""
        try:
            url = f"{settings.get_capital_host()}/api/v1/markets/{epic}"
            response = await settings.session.get(url, headers=memory.capital_auth_header)
            
            if response.status_code != 200:
                await Logger.app_log(
                    title="API_ERR",
                    message=f"Failed to fetch {epic} prices: {response.status_code}"
                )
                return 0.0, 0.0
            
            data = response.json()
            snapshot = data.get("snapshot", {})
            ask = snapshot.get("offer", 0.0)
            bid = snapshot.get("bid", 0.0)
            if not ask or not bid:
                await Logger.app_log(title="NO_DATA", message=f"No ask/bid for {epic}")
                return 0.0, 0.0
            
            return float(ask), float(bid)
        
        except Exception as e:
            await Logger.app_log(title="API_ERR", message=f"{epic}: {str(e)}")
            return 0.0, 0.0
    
    
async def open_trade(epic: str, size: float, trade_direction: TradeDirection, retry: int = 0) -> str | bool:
    try:
        # Build payload
        payload = {
            "epic": epic,
            "direction": trade_direction.value,
            "size": str(size),  # Updated to "size" per docs
        }

        response = await settings.session.post(
            f"{settings.get_capital_host()}/api/v1/positions",
            headers= memory.capital_auth_header,
            json=payload
        )
        if response.status_code == 200:
            data = response.json()
            reference = data["dealReference"]
            deal_id = await get_epic_deal_id(epic, size, trade_direction)
            memory.update_deal_id(deal_id) # Update deal ID in memory
            if deal_id:
                await Logger.app_log(
                    title=f"OPENED_{trade_direction.value}_TRADE",
                    message=f"{size} size of {epic} ({reference})"
                )
            else:
                raise ValueError("Could not retrieve deal ID")
            
            return deal_id
    except Exception as e:
        await Logger.app_log(title=f"{epic}_OPEN_TRADE_ERR", message=str(e))
        if retry < settings.MAX_RETRY_ATTEMPTS:
            await asyncio.sleep(settings.RETRY_SLEEP_TIME)
            return await open_trade(epic, size, trade_direction, retry + 1)
        return False
    

async def confirm_trade_closed(epic: str, deal_id: str,) -> bool:
    try:
        await asyncio.sleep(3)
        open_positions = await get_open_positions()
        for position in open_positions:
            if position["epic"] == epic and position["deal_id"] == deal_id:
                return False
        return True
    except Exception as e:
        await Logger.app_log(title="CONFIRM_CLOSE_ERR", message=str(e))
        return False


async def close_trade(epic: str, size: float, deal_id: str, position_mode: TradeMode, retry: int = 0) -> bool:
    try:
        from database import delete_position
        
        response = await settings.session.delete(
            f"{settings.get_capital_host(position_mode)}/api/v1/positions/{deal_id}",
            headers= memory.capital_auth_header,
        )
        if response.status_code == 200:
            data = response.json()
            await Logger.app_log(
                title="CLOSE_SUCCESS",
                message=f"Closed {size} of {epic}: {data}"
            )

            close_deal_id = data.get("dealReference", False)
            if not close_deal_id:
                raise ValueError(f"Trade still open: {close_deal_id}")
            
            if not await confirm_trade_closed(epic, deal_id):
                raise ValueError("Trade not closed yet")
            
            memory.remove_deal_id(deal_id)  # Remove deal ID from settings
            await delete_position(deal_id) # remove position from DB if already closed

            return True
            
        raise ValueError(f"Failed to close trade: {response.status_code} => {response.text}")
    
    except Exception as e:
        await Logger.app_log(title=f"{epic}_CLOSE_TRADE_ERR", message=str(e))
        if retry < settings.MAX_RETRY_ATTEMPTS:
            await asyncio.sleep(settings.RETRY_SLEEP_TIME)
            return await close_trade(epic, size, deal_id, position_mode, retry + 1)
        return False
        
   

async def update_markets() -> None:
    try:
        epics = set()
        instruments = {} # Use a set to avoid duplicates
        response = await settings.session.get(
            f"{settings.get_capital_host()}/api/v1/markets",
            headers=memory.capital_auth_header
        )
        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", [])
            for market in markets:
                epics.add(market["epic"])
                instruments[market["epic"]] = market["instrumentType"]
        else:
            await Logger.app_log(
                title="MARKET_DATA_FAIL",
                message=f"Status {response.status_code}: {response.text}"
            )
            return []
        memory.update_epics(epics=list(sorted(epics)), instruments=instruments)
        
    except Exception as e:
        await Logger.app_log(title="MARKET_DATA_ERR", message=str(e))  
    
    
    
    
async def get_account_preferences() -> dict:
    try:
        response = await settings.session.get(
            f"{settings.get_capital_host()}/api/v1/accounts/preferences",
            headers=memory.capital_auth_header
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            await Logger.app_log(
                title="PREF_FETCH_FAIL",
                message=f"Status {response.status_code}: {response.text}"
            )
            return {}
    except Exception as e:
        await Logger.app_log(title="PREF_GET_ERR", message=str(e))
        return {}
        
        
        
async def set_account_preferences(leverages: dict = None, hedging_mode: bool = None) -> bool:
    try:
        # Get current preferences first to modify only what’s provided
        current_prefs = await get_account_preferences()
        if not current_prefs:
            await Logger.app_log(
                title="PREF_SET_FAIL",
                message="Couldn’t fetch current preferences"
            )
            return False

        # Build payload with current values as fallback
        payload = {
            "leverages": leverages if leverages is not None else current_prefs.get("leverages", {}),
            "hedgingMode": hedging_mode if hedging_mode is not None else current_prefs.get("hedgingMode", False)
        }
    
        response = await settings.session.put(
            f"{settings.get_capital_host()}/api/v1/accounts/preferences",
            headers= memory.capital_auth_header,
            json=payload
        )
        if response.status_code == 200:
            await Logger.app_log(
                title="PREF_SET_SUCCESS",
                message=f"Updated preferences: {payload}"
            )
            return True
        else:
            await Logger.app_log(
                title="PREF_SET_FAIL",
                message=f"Status {response.status_code}: {response.text}"
            )
            return False
    except Exception as e:
        await Logger.app_log(title="PREF_SET_ERR", message=str(e))
        return False 
    
    
    
async def get_epic_hours(epic: str):
        try:
            response = await settings.session.get(
                f"{settings.get_capital_host()}/api/v1/markets/{epic}", 
                headers= memory.capital_auth_header,
                )
            if response.status_code != 200:
                await Logger.app_log(
                    title="EPIC_HRS_ERR",
                    message=f"Failed to fetch {epic} hours: {response.status_code}"
                )
                return None
            
            data = response.json()
            instrument = data.get("instrument", {})
            hours = instrument.get("openingHours", {})
            if not hours:
                await Logger.app_log(title="NO_DATA", message=f"No hours for {epic}")
                return None
            return hours
        
        except Exception as e:
            await Logger.app_log(title="EPIC_HRS_ERR", message=f"{epic}: {str(e)}")
            return None
           
def parse_time_str(t: str, now: datetime):
    # Accept HH:MM or HH:MM:SS
    fmt = "%H:%M:%S" if t.count(":") == 2 else "%H:%M"
    parsed = datetime.strptime(t, fmt).time()
    return now.replace(hour=parsed.hour, minute=parsed.minute, second=parsed.second, microsecond=0)
     
                     
async def is_market_closed(epic: str, min: int = 2) -> bool:
        try:
            hours = memory.trading_hours.get(epic, {})
            if not hours:
                hours = memory.trading_hours[epic] = await get_epic_hours(epic)
            
            # print("Hours => ", hours)
            now_utc = datetime.utcnow()
            day_key = now_utc.strftime("%a").lower()
            day_hours = hours.get(day_key, [])

            if not day_hours:
                return True   # never opens today

            for rng in day_hours:
                start_str, end_str = rng.split(" - ")

                start_time_today = parse_time_str(start_str, now_utc)
                end_time_today   = parse_time_str(end_str, now_utc)

                if end_time_today < start_time_today:
                    end_time_today += timedelta(days=1)

                if start_time_today <= now_utc < end_time_today:
                    time_remaining_minutes = (end_time_today - now_utc).total_seconds() / 60
                    return time_remaining_minutes <= min

            return True

        except Exception as e:
            await Logger.app_log(title="MARKET_HRS_ERR", message=f"{epic}: {str(e)}")
            return False
     
                     
async def is_market_eod_close(epic: str, min: int = 2) -> bool:
    try:
        hours = memory.trading_hours.get(epic, {})
        if not hours:
            hours = memory.trading_hours[epic] = await get_epic_hours(epic)

        now_utc = datetime.utcnow()
        day_key = now_utc.strftime("%a").lower()
        day_hours = hours.get(day_key, [])

        # Market closed the whole day
        if not day_hours:
            return True

        # Use only LAST trading range for today
        start_str, end_str = day_hours[-1].split(" - ")

        start_time_today = parse_time_str(start_str, now_utc)
        end_time_today = parse_time_str(end_str, now_utc)

        # Handle overnight session (e.g., 22:00 - 05:00 next day)
        if end_time_today < start_time_today:
            end_time_today += timedelta(days=1)

        # Check if we're currently in that final session
        if start_time_today <= now_utc < end_time_today:
            time_remaining_minutes = (end_time_today - now_utc).total_seconds() / 60
            return time_remaining_minutes <= min

        # past the final session => market closed for day
        if now_utc >= end_time_today:
            return True

        # market still widely open
        return False

    except Exception as e:
        await Logger.app_log(title="MARKET_EOD_ERR", message=f"{epic}: {str(e)}")
        return False

        

async def is_market_eow_close(epic: str, min: int = 2) -> bool:
    try:
        hours = memory.trading_hours.get(epic, {})
        if not hours:
            hours = memory.trading_hours[epic] = await get_epic_hours(epic)

        # find last trading window of the week
        weekdays = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
        last_day = None
        last_range = None

        for day in reversed(weekdays):
            day_hours = hours.get(day, [])
            if day_hours:
                last_day = day
                last_range = day_hours[-1]
                break
        if not last_range:
            return False 

        now_utc = datetime.utcnow()
        start_str, end_str = last_range.split(" - ")

        # align to actual date of the last trading day
        today_key = now_utc.strftime("%a").lower()
        day_index_now = weekdays.index(today_key)
        day_index_last = weekdays.index(last_day)

        # calculate target end datetime
        days_diff = (day_index_last - day_index_now) % 7
        ref_date = now_utc + timedelta(days=days_diff)

        start_time = parse_time_str(start_str, ref_date)
        end_time = parse_time_str(end_str, ref_date)
        if end_time < start_time:
            end_time += timedelta(days=1)

        # only relevant if we're on the last day
        if today_key == last_day:
            if start_time <= now_utc < end_time:
                time_remaining_minutes = (end_time - now_utc).total_seconds() / 60
                return time_remaining_minutes <= min

        return False

    except Exception as e:
        await Logger.app_log(title="MARKET_EOW_ERR", message=f"{epic}: {str(e)}")
        return False

        

async def portfolio_balance():
    try:
        header = memory.capital_auth_header
        response = await settings.session.get(f"{settings.get_capital_host()}/api/v1/accounts", headers=header)
        if response.status_code == 200:
            data = response.json()
            portfolio = data["accounts"][0]
            memory.portfolio = portfolio
            return portfolio
    except Exception as e:
        await Logger.app_log(title="PORTFOLIO_ERR", message=str(e))
        return memory.portfolio
