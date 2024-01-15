from game_server.adapters.logic.game_logic_adapter import GameLogicAdapter
from game_server.use_cases.game_service import GameService
from game_server.adapters.cache.game_cache_adaapter import GameCacheAdapter
from game_server.use_cases.game_service import GameService
from game_server.entities.objects.player import Player
from game_server.entities.objects.game import Game
from game_server.entities.objects.dealer import Dealer
import asyncio
from websockets.server import serve
import json
import uuid

connected_clients = {}
MAX_CONNECTIONS = 4
connection_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)

game = GameService(logic=GameLogicAdapter(), cache=GameCacheAdapter())
game_status = Game(
    players=game.cache.load_players_data(),
    dealer=Dealer(),
    cards_deck=game.game_logic.shuffle_cards(),
    isRoundStarting=False,
    isRoundFinished=True
)
game.cache.save_game_status(game=game_status)


async def broadcast(message):
    # Broadcast the message to all connected clients
    for client in connected_clients.values():
        await client.send(message)

async def send_time_message():
    cont = 30
    while cont> 0:
        message = "the game is starting in {time} seconds".format(time=cont)
        print(message)
        message = json.dumps(
            {
                "type": "time",
                "content": message
            }
        )
        await broadcast(message)
        await asyncio.sleep(5)
        cont -= 5


async def send_first_cards_message(game_status):
    message = "dealer cards are: {cards}".format(cards=" ".join(map(str, game_status.dealer.cards)))
    print(message)
    for player in game_status.players:
        message = "player {name} cards are: {cards}".format(name=player.name,
                                                             cards=" ".join(map(str, player.cards)))
        print(message)
    message = json.dumps(
        {
            "type": "time",
            "content": game_status
        }
    )
    await broadcast(message)

async def starting_game():
    if (game.cache.get_game_status().isRoundFinished == True and
        len(game.cache.load_players_data())):
        game_status = game.cache.get_game_status()
        game_status.isRoundFinished = False
        game.cache.save_game_status(game=game_status)
        await send_time_message()
        game_status = game.cache.get_game_status()
        game_status.isRoundStarting = False
        game.cache.save_game_status(game=game_status)

        game.load_game()

        game.get_cards()
        game_status = game.cache.get_game_status()
        await send_first_cards_message(game_status.__dict__)
        print(game_status)

async def game_run(websocket):
    async with connection_semaphore:
        client_id = str(uuid.uuid4())
        connected_clients[client_id] = websocket

        try:
            async for message in websocket:
                msg = json.loads(message)
                if msg["type"] == "login" and game.cache.get_game_status().isRoundFinished == True:
                    game.cache.save_players_data(players=[
                        Player(
                            name=msg["name"],
                            player_id=msg["player_id"],
                            bet=0,
                            credit=100
                        )
                    ] + game.cache.load_players_data())
                    client_id = msg["player_id"]
                    connected_clients[client_id] = websocket
                    print("new user login: {player_id}".format(player_id=client_id))

                if msg["type"] == "play" and game.cache.get_game_status().isRoundFinished == False:
                    pass
                
                await starting_game()
        except Exception as e:
            print(e)
            del connected_clients[client_id]

async def main():
    async with serve(game_run, "localhost", 8765):
        print("server started")
        await asyncio.Future()  # run forever

asyncio.run(main())