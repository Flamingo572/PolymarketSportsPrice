from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from src.bot_manager import bot_manager

app = FastAPI()

# Mount static files (we'll create static/index.html next)
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html", "r") as f:
        return f.read()

@app.websocket("/ws/{slug}")
async def websocket_endpoint(websocket: WebSocket, slug: str):
    await websocket.accept()
    
    async def callback(payload):
        await websocket.send_json(payload)

    success = await bot_manager.start_tracking(slug, callback)
    if not success:
        await websocket.send_json({"type": "error", "message": f"Could not find IDs for slug: {slug}"})
        await websocket.close()
        return

    try:
        # Keep connection open and wait for messages from client (if any)
        while True:
            data = await websocket.receive_text()
            # We don't expect much from client, but we can handle commands here
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        print(f"Client disconnected for slug: {slug}")
    finally:
        await bot_manager.stop_tracking(slug, callback)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
