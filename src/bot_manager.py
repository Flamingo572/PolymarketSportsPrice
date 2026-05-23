import asyncio
import websockets
import json
import os
from py_clob_client.client import ClobClient
import src.findIDs as findIDs
from dotenv import load_dotenv

load_dotenv()

class BotManager:
    def __init__(self):
        self.active_tasks = {} # slug -> {tasks, clients: set(callbacks)}
        self.shared_state = {} # slug -> {market_data, sports_data}
        self.private_key = os.getenv("POLYMARKET_PRIVATE_KEY", "YOUR_PRIVATE_KEY_HERE")
        self.proxy_address = os.getenv("POLYMARKET_PROXY_ADDRESS", "")

    def setup_clob_auth(self):
        host = "https://clob.polymarket.com"
        # signature_type 1 is for Email/Magic accounts, 2 is for Browser Wallets. 
        # Defaulting to 1 as seen in existing scripts.
        client = ClobClient(host, key=self.private_key, chain_id=137, signature_type=1, funder=self.proxy_address)
        keys = client.derive_api_key()
        return {
            "apiKey": keys.api_key, 
            "secret": keys.api_secret, 
            "passphrase": keys.api_passphrase
        }

    async def broadcast(self, slug, message_type, data):
        if slug in self.active_tasks:
            payload = {
                "type": message_type,
                "slug": slug,
                "data": data
            }
            # Also check for trade signals
            signal = self.check_trade_signal(slug, message_type, data)
            if signal:
                payload["signal"] = signal

            for callback in self.active_tasks[slug]["clients"]:
                try:
                    await callback(payload)
                except Exception as e:
                    print(f"Error in broadcast callback: {e}")

    def check_trade_signal(self, slug, message_type, data):
        state = self.shared_state.get(slug)
        if not state:
            return None
        
        if message_type == "market":
            state["market_data"] = data
        elif message_type == "sports":
            old_sports = state.get("sports_data")
            state["sports_data"] = data
            
            if old_sports and old_sports.get("score") != data.get("score"):
                if state.get("market_data"):
                    return {
                        "message": "Score changed while market data available!",
                        "old_score": old_sports.get("score"),
                        "new_score": data.get("score")
                    }
        return None

    async def listen_market(self, slug, asset_ids, auth):
        url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        try:
            async with websockets.connect(url) as ws:
                sub_payload = {"assets_ids": asset_ids, "type": "market"}
                await ws.send(json.dumps(sub_payload))
                print(f"✅ [{slug}] Connected to Market WebSocket")

                async def ping_loop():
                    while True:
                        await asyncio.sleep(10)
                        try:
                            await ws.send("PING")
                        except:
                            break
                
                asyncio.create_task(ping_loop())

                async for message in ws:
                    try:
                        data = json.loads(message)
                        # The market WS returns a list sometimes or a single dict
                        if isinstance(data, list):
                            for item in data:
                                await self.broadcast(slug, "market", item)
                        else:
                            await self.broadcast(slug, "market", data)
                    except json.JSONDecodeError:
                        pass # Ignore PONG or invalid JSON
        except Exception as e:
            print(f"Market WebSocket error for {slug}: {e}")

    async def listen_sports(self, slug, game_id):
        url = "wss://sports-api.polymarket.com/ws"
        try:
            async with websockets.connect(url) as ws:
                print(f"✅ [{slug}] Connected to Sports WebSocket")
                async for message in ws:
                    if message == "PING":
                        await ws.send("PONG")
                    else:
                        try:
                            data = json.loads(message)
                            if data.get("gameId") == game_id:
                                await self.broadcast(slug, "sports", data)
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            print(f"Sports WebSocket error for {slug}: {e}")

    async def start_tracking(self, slug, callback):
        if slug not in self.active_tasks:
            print(f"Starting new tracking tasks for slug: {slug}")
            try:
                game_id, clob_token_ids, outcomes = findIDs.findIdsBySlug(slug)
                # Parse asset ID robustly
                if isinstance(clob_token_ids, list):
                    clob_token_id = clob_token_ids[0]
                elif isinstance(clob_token_ids, str):
                    if clob_token_ids.startswith("["):
                        import re
                        match = re.search(r'"([^"]+)"', clob_token_ids)
                        clob_token_id = match.group(1) if match else clob_token_ids
                    else:
                        clob_token_id = clob_token_ids
                else:
                    clob_token_id = str(clob_token_ids)

                auth = self.setup_clob_auth()
                asset_ids = [clob_token_id]
                
                self.shared_state[slug] = {"market_data": None, "sports_data": None}
                
                market_task = asyncio.create_task(self.listen_market(slug, asset_ids, auth))
                sports_task = asyncio.create_task(self.listen_sports(slug, game_id))
                
                self.active_tasks[slug] = {
                    "tasks": [market_task, sports_task],
                    "clients": {callback},
                    "meta": {"game_id": game_id, "asset_id": clob_token_id, "outcomes": outcomes}
                }
            except Exception as e:
                print(f"Failed to start tracking for {slug}: {e}")
                return False
        else:
            self.active_tasks[slug]["clients"].add(callback)
        
        return True

    async def stop_tracking(self, slug, callback):
        if slug in self.active_tasks:
            self.active_tasks[slug]["clients"].discard(callback)
            if not self.active_tasks[slug]["clients"]:
                print(f"No more clients for {slug}, stopping tasks.")
                for task in self.active_tasks[slug]["tasks"]:
                    task.cancel()
                del self.active_tasks[slug]
                if slug in self.shared_state:
                    del self.shared_state[slug]

bot_manager = BotManager()
