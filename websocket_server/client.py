import asyncio
from websockets.sync.client import connect
import json
import uuid

player_id = str(uuid.uuid4())

def is_convertible_to_int(value):
    try:
        int_value = int(value)
        return True
    except ValueError:
        return False
        
def login(websocket):
    name = input("type your name: ")
    msg = json.dumps(
        {
            "type": "login",
            "name": name,
            "player_id": player_id
        }
    )
    websocket.send(msg)
    return name

def client():
    with connect("ws://localhost:8765") as websocket:
        name = login(websocket)
        while True:
            msg = json.loads(websocket.recv())
            
            if msg.get("type", None) == "time":
                msg = json.loads(websocket.recv())
                print("{message}".format(message=msg["content"]))
            
            if msg.get("type", None) == "cards":
                print("dealer cards: {cards}".format(cards=msg["content"]["dealer"]["cards"]))
                for player in msg["content"]["players"]:
                    print("player {name} cards: {cards}".format(name=player["name"], cards=player["cards"]))
            
            if msg.get("type", None) == "play":
                if bool(msg.get("your_turn")) == True:
                    print("Is your turn")
                    
                    is_valid = False
                    while is_valid == False:
                        value = input("type 1 to request a hit, type 2 to stand: ")
                        increase_bet = input("how much would you increase your bet: ")
                        action_map = {"1": "hit", "2": "stand"}
                        if (value == "1" or value == "2") and is_convertible_to_int(increase_bet):
                            is_valid = True
                        else:
                            print("invalid input")
                    sending_msg = json.dumps(
                        {
                            "type": "play",
                            "action": action_map[value],
                            "player_name": name,
                            "bet": increase_bet,
                            "player_id": player_id
                        }
                    )
                    websocket.send(sending_msg)
                else:
                    print(msg["content"])
            
            if msg.get("type", None) == "dealer":
                print("{message}".format(message=msg["content"]))
            
            if msg.get("type", None) == "finish":
                print("{message}".format(message=msg["content"]))

client()