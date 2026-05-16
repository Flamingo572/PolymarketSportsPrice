import json
import time
from websocket import WebSocketApp
import threading

class PolymarketSportsWS:
    def __init__(self, gameId):
        self.url = "wss://sports-api.polymarket.com/ws"
        self.ws = WebSocketApp(
            self.url, 
            on_open= self.on_open,
            on_message= self.on_message,
            on_close= self.on_close,
            on_error= self.on_error
                               )
        self.gameId = gameId
    
    def on_open(self, ws):
        print("Broadcast has started")
    
    def on_message(self, ws, message):
        data = json.loads(message)
        # print(data)
        if message == "PING":
            print(message)
            self.ws.send("PONG")
        else:
            self.dealWithMessage(data)
            # homeTeam = data.get("homeTeam")
            # awayTeam = data.get("awayTeam")
            # score = data.get("score")
            # elapsedTime = data.get("elapsed")
            # timeForUpdate = data.get("eventState").get("updatedAt")
            # print(f"Teams: {homeTeam} vs {awayTeam}\nScore: {score}\nElapsed: {elapsedTime}\n Time Updated: {timeForUpdate}")

    def on_close(self, ws, close_status_code, close_msg):
        print("closing connection")
        exit(0)

    def on_error(self, ws, error):
        print("Error: ", error)
        exit(1)
    
    def run(self):
        self.ws.run_forever()

    def dealWithMessage(self, data):
        print(data)
        if data.get("gameId") == self.gameId:
            print("#$%^&*")
            print(data)

def startMarketRead(gameId):
    sportsBot = PolymarketSportsWS(gameId)
    sportsBot.run()
    
        
        