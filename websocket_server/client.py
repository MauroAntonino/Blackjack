import asyncio
from websockets.sync.client import connect
import json
import uuid

def hello():
    with connect("ws://localhost:8765") as websocket:
        name = input("type your name: ")
        msg = json.dumps(
            {
                "type": "login",
                "name": name,
                "player_id": str(uuid.uuid4())
            }
        )
        websocket.send(msg)
        msg = json.loads(websocket.recv())
        while msg.get("type", None) == "time":
            msg = json.loads(websocket.recv())
            print("{message}".format(message=msg["content"]))
        
hello()