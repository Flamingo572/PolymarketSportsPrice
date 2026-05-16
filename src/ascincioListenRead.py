import asyncio
import websockets
import json
from py_clob_client.client import ClobClient
import src.findIDs as findIDs

# --- SHARED STATE FOR YOUR TRADING BOT ---
shared_state = {
    "market_data": None,
    "sports_data": None
}

async def executeTradeLogic(source, message):
    """
    Central hub for processing updates. It updates the state and checks 
    if conditions are met to execute a trade.
    """
    data = ""
    if(not isinstance(message, dict)):

        try:
            data = json.loads(message)
        except:
            print(f"!?!?!?!ERROR!?!?!?!{message}")
            return
    else:
        data = message
    
    if source == "market":
        shared_state["market_data"] = data
    elif source == "sports":
        print(data)
        if(shared_state["sports_data"] != None):
            print(shared_state["sports_data"])
            if(shared_state["sports_data"]["score"] != data['score'] and shared_state["market_data"] is not None and shared_state["sports_data"] is not None):
                    print(f"\n🚀 [TRADE SIGNAL] Triggered by {source.upper()} update!")
                    print(shared_state["market_data"])
                    print(shared_state["sports_data"])
                    # Insert your mathematical comparisons or trade execution API calls here
                    shared_state["market_data"] = None
                    shared_state["sports_data"] = None
        shared_state["sports_data"] = data
        
            
        
    


# --- 1. CLOB MARKET WEBSOCKET ---
async def listenMarket(asset_ids, auth):
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    
    async with websockets.connect(url) as ws:
        # Send initial subscription payload
        subPayload = {"assets_ids": asset_ids, "type": "market"}
        await ws.send(json.dumps(subPayload))
        print("✅ Connected to Market WebSocket")

        # Start a background task to ping every 10 seconds
        async def pingLoop():
            while True:
                await asyncio.sleep(10)
                try:
                    await ws.send("PING")
                except:
                    break
        
        # Run the ping loop alongside our listening loop
        asyncio.create_task(pingLoop())

        # Listen for market updates
        async for message in ws:
            # Send the message to our central trading hub
            await executeTradeLogic("market", message)


# --- 2. SPORTS WEBSOCKET ---
async def listenSports(gameId):
    url = "wss://sports-api.polymarket.com/ws"
    
    async with websockets.connect(url) as ws:
        print("✅ Connected to Sports WebSocket")
        
        async for message in ws:
            # Handle Polymarket's specific PING/PONG for the sports socket
            if message == "PING":
                await ws.send("PONG")
            else:
                data = json.loads(message)
                # Filter strictly by the gameId we care about
                if data.get("gameId") == gameId:
                # Send to central trading hub
                    await executeTradeLogic("sports", data)


# --- INITIALIZATION & ORCHESTRATION ---
def setupClOBAuth():
    """Synchronous function to generate your Polymarket auth keys."""
    host = "https://clob.polymarket.com"
    key = "YOUR_PRIVATE_KEY_HERE"
    chain_id = 137
    proxy_address = '' 

    client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1, funder=proxy_address)
    keys = client.derive_api_key()
    
    return {
        "apiKey": keys.api_key, 
        "secret": keys.api_secret, 
        "passphrase": keys.api_passphrase
    }

async def main(slug):
    
    gameId, clobTokenIds, outcomes = findIDs.findIdsBySlug(slug)
    clobTokenId = clobTokenIds[clobTokenIds.index('\"')+1: (clobTokenIds[clobTokenIds.index('\"')+1: ].index('\"')) + 2]
    
    # 2. Get Polymarket Auth
    auth = setupClOBAuth()
    asset_ids = [clobTokenId]
    
    print(f"Starting bot for Game ID: {gameId} | Asset ID: {clobTokenId}")

    await asyncio.gather(
        listenMarket(asset_ids, auth),
        listenSports(gameId)
    )

async def analyzeMarket(channel, message):
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print("Received invalid JSON.")
        return
    if(isinstance(data, list)):
        data = data[0]
    event_type = data.get('event_type')


    # ---------------------------------------------------------
    # 1. BOOK: Initial Snapshot 
    # Emitted when you first subscribe or on major book changes
    # ---------------------------------------------------------
    if event_type == "book":
        asset_id = data.get("asset_id")
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        # Grab the top of the book just to see where the market is at
        top_bid = bids[0] if bids else None
        top_ask = asks[0] if asks else None
        
        print(f"\n[BOOK SNAPSHOT] Asset: {asset_id}")
        print(f"Top Bid: {top_bid} | Top Ask: {top_ask}")
        # -> Logic: Initialize or completely overwrite your local orderbook here.

    # ---------------------------------------------------------
    # 2. PRICE CHANGE: Order modifications, additions, or pulls
    # ---------------------------------------------------------
    elif event_type == "price_change":
        changes = data.get("price_changes", [])
        
        for change in changes:
            asset_id = change.get("asset_id")
            side = change.get("side") # "BUY" or "SELL"
            price = float(change.get("price"))
            size = float(change.get("size"))
            
            if size == 0.0:
                print(f"[-] [PRICE CHANGE] Liquidity Removed: {side} at ${price}")
                # -> Logic: Delete this price level from your local book.
            else:
                print(f"[+] [PRICE CHANGE] Liquidity Updated: {side} at ${price} (Size: {size})")
                # -> Logic: Update the size for this price level in your local book.
            print(change)
            bestBid = change.get("best_bid")
            bestAsk = change.get("best_ask")
            print(f"Best Bid Is: {bestBid}; Best Ask Is {bestAsk}")
        

    # ---------------------------------------------------------
    # 3. LAST TRADE PRICE: Actual trade executions
    # ---------------------------------------------------------
    elif event_type == "last_trade_price":
        asset_id = data.get("asset_id")
        price = float(data.get("price"))
        size = float(data.get("size"))
        side = data.get("side") 
        
        print(f"[$] [TRADE EXECUTED] {size} shares at ${price} ({side} side)")
        # -> Logic: Update your trading indicators, calculate volume, or check if your own limit orders should have filled.

    else:
        # Silently ignore anything else
        pass

if __name__ == "__main__":
    slug = "epl-sun-ful-2026-02-22"

    try:
        asyncio.run(main(slug))
    except KeyboardInterrupt:
        print("\nShutting down trading bot...")