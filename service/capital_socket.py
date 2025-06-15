import websockets, asyncio, json
from memory import memory
from logger import Logger
from .capital_api import get_last_api_ask_bid


class CapitalSocket:
    def __init__(self):
        self.websocket = None
        self.running = False
        self.subscribed_epics = set()
        self._listen_task = None

    
    async def connect_websocket(self):
        """Connect to Capital.com WebSocket if not already connected."""
        if not self.websocket:
            uri = "wss://api-streaming-capital.backend-capital.com/connect"
            self.websocket = await websockets.connect(uri, ping_interval=60, ping_timeout=30)
            self.running = True
            
            if not self._listen_task or self._listen_task.done():
                self._listen_task = asyncio.create_task(self._listen())
            await Logger.app_log(title="WS_CONNECT", message="WebSocket connected")
            
    async def ping_socket(self):
        """Ping socket service to keep connection alive."""
        try:
            ping_msg = {
                "destination": "ping",
                "correlationId": "ping_XGXXXTX",
                "cst": memory.capital_auth_header["CST"],
                "securityToken": memory.capital_auth_header["X-SECURITY-TOKEN"]
            }
            
            if self.running:
                await self.websocket.send(json.dumps(ping_msg))
            
        except Exception as e:
            await Logger.app_log(title="PING_ERR", message=f"Ping failed: {str(e)}")
            self.running = False
            
            
    async def subscribe_to_epic(self, epic: str):
        """Subscribe to real-time data for a given epic."""
        try:
            await self.connect_websocket()
            if epic in self.subscribed_epics:
                await Logger.app_log(title="SUBSCRIBE_SKIP", message=f"{epic} already subscribed")
                return
            
            subscribe_msg = {
                "destination": "marketData.subscribe",
                "correlationId": f"epic_sub_{epic}",
                "cst": memory.capital_auth_header["CST"],
                "securityToken": memory.capital_auth_header["X-SECURITY-TOKEN"],
                "payload": {"epics": [epic]}
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            # updated lastest ask - bid data
            ask, bid = await get_last_api_ask_bid(epic)
            memory.update_market_data(epic=epic, ask=ask, bid=bid, timestamp=0)
            self.subscribed_epics.add(epic)
            await Logger.app_log(title="SUBSCRIBE_SENT", message=f"Subscribed to {epic}")
            
        except Exception as e:
            await Logger.app_log(title="SUBSCRIBE_ERR", message=f"{epic}: {str(e)}")


    async def unsubscribe_from_epic(self, epic: str):
        """Unsubscribe from real-time data for a given epic."""
        try:
            if not self.websocket:
                await Logger.app_log(title="UNSUBSCRIBE_ERR", message="No active WebSocket")
                return
            if epic not in self.subscribed_epics:
                await Logger.app_log(title="UNSUBSCRIBE_SKIP", message=f"{epic} not subscribed")
                return
            
            unsubscribe_msg = {
                "destination": "marketData.unsubscribe",
                "correlationId": f"epic_sub_{epic}",
                "cst": memory.capital_auth_header["CST"],
                "securityToken": memory.capital_auth_header["X-SECURITY-TOKEN"],
                "payload": {"epics": [epic]}
            }
            await self.websocket.send(json.dumps(unsubscribe_msg))
            self.subscribed_epics.remove(epic)
            await Logger.app_log(title="UNSUBSCRIBE_SENT", message=f"Unsubscribed from {epic}")
        except Exception as e:
            await Logger.app_log(title="UNSUBSCRIBE_ERR", message=f"{epic}: {str(e)}")


    async def _listen(self):
        """Listen for incoming WebSocket messages and handle reconnections."""
        try:
            while self.running and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=300)
                    data = json.loads(message)

                    if data["destination"] == "marketData.subscribe":
                        await Logger.app_log(
                            title="SUBSCRIBE_CONFIRM",
                            message=f"Subscription: {data['payload']['subscriptions']}"
                        )
                    elif data["destination"] == "marketData.unsubscribe":
                        await Logger.app_log(
                            title="UNSUBSCRIBE_CONFIRM",
                            message=f"Unsubscription: {data['payload']['subscriptions']}"
                        )
                    elif data["destination"] == "quote":
                        payload = data["payload"]
                        memory.update_market_data(
                            epic=payload["epic"],
                            ask=payload["ofr"],
                            bid=payload["bid"],
                            timestamp=payload["timestamp"]
                        )

                except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosedError) as e:
                    await Logger.app_log(title="WS_LISTEN_ERR", message=str(e))
                    break  # Exit inner loop to reconnect

        except Exception as e:
            await Logger.app_log(title="WS_LISTEN_ERR", message=f"Unhandled: {str(e)}")

        finally:
            self.running = False
            if self.websocket:
                try:
                    await self.websocket.close()
                except Exception as close_error:
                    await Logger.app_log(title="WS_CLOSE_ERR", message=str(close_error))
                self.websocket = None

            self._listen_task = None  # Mark task as finished
            await Logger.app_log(title="WS_RECONNECT", message="Reconnecting WebSocket...")
            await asyncio.sleep(1)  # Prevent reconnect flood

            # Resubscribe to previous epics after reconnect
            epics = list(self.subscribed_epics)
            self.subscribed_epics.clear()
            for epic in epics:
                await self.subscribe_to_epic(epic)
                await asyncio.sleep(0.5)



capital_socket = CapitalSocket()