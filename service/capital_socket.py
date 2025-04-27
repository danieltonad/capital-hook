import websockets, asyncio, json
from memory import memory
from logger import Logger
from .capital_api import get_last_api_ask_bid


class CapitalSocket:
    def __init__(self):
        self.websocket = None
        self.running = False
        self.subscribed_epics = set()

    
    async def connect_websocket(self):
        """Connect to Capital.com WebSocket if not already connected."""
        if not self.websocket:
            uri = "wss://api-streaming-capital.backend-capital.com/connect"
            self.websocket = await websockets.connect(uri)
            self.running = True
            asyncio.create_task(self._listen())  # Start listening in background
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
        """Background task to process incoming WebSocket messages."""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
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
                    await memory.update_market_data(epic=payload["epic"], ask=payload["ofr"], bid=payload["bid"], timestamp=payload["timestamp"])
                else:
                    await asyncio.sleep(5)
                
        except Exception as e:
            await Logger.app_log(title="WS_LISTEN_ERR", message=str(e))
            self.running = False
            await self.websocket.close()
            # reconnect
            self.websocket = None
            await self.connect_websocket()
            print("WebSocket connection closed, attempting to reconnect...")
            epics = self.subscribed_epics
            self.subscribed_epics = set()
            for epic in epics:
                await self.subscribe_to_epic(epic)



capital_socket = CapitalSocket()