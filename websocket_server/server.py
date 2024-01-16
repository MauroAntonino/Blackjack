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
import os

first_time = True
connected_clients = {}
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT"))
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS"))
connection_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)
WAITING_TIME = 25

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
    time = WAITING_TIME
    while time > 0:
        message = "the game is starting in {time} seconds".format(time=time)
        print(message)
        message = json.dumps(
            {
                "type": "time",
                "content": message
            }
        )
        await broadcast(message)
        await asyncio.sleep(5)
        time -= 5

async def send_first_cards_message(game_status):
    cards = game_status.dealer.cards
    cards[1] = "*"
    message = "dealer cards are: {cards}".format(cards=" ".join(map(str, cards)))
    print(message)
    for player in game_status.players:
        message = "player {name} cards are: {cards}".format(name=player.name,
                                                             cards=" ".join(map(str, player.cards)))
    game_status = game.cache.get_game_as_dict(game_status)
    
    players = game.cache.load_players_data()
    game_status["players"] = [  game.cache.get_palyer_as_dict(player)  for player in players ]
    message = json.dumps(
        {
            "type": "cards",
            "content": game_status
        }
    )
    await broadcast(message)

async def playing_blackjack(player_id):
    print("player with id {id} round".format(id=player_id))
    for client in connected_clients.keys():
        message_to_others = json.dumps(
            {
                "type": "play",
                "your_turn": False,
                "content": "Wait other player turn"
            }
        )
        if client != player_id:
            await connected_clients[client].send(message_to_others)
        else:
            message_to_player = json.dumps(
                {
                    "type": "play",
                    "your_turn": True,
                    "client": client
                }
            )
            await connected_clients[client].send(message_to_player)

async def clean_players_cache(game_status):
    players = game.cache.load_players_data()
    new_players = [player for player in players if player.player_id in connected_clients.keys()]
    game.cache.save_players_data(players=new_players)


async def starting_game():
    if (game.cache.get_game_status().isRoundFinished == True and
        len(game.cache.load_players_data())):
        await send_time_message()
        game_status = game.cache.get_game_status()
        game_status.isRoundFinished = False
        game.cache.save_game_status(game=game_status)
        await clean_players_cache(game_status)

        game.load_game()

        game.get_cards()
        game_status = game.cache.get_game_status()
        await send_first_cards_message(game_status)
        await playing_blackjack(game_status.players[0].player_id)
        
def get_player_with_id(player_id):
    game_status = game.cache.get_game_status()
    player = None
    print(game_status.players)
    for current_player in game_status.players:
        print(current_player.player_id == player_id)
        if current_player.player_id == player_id:
            player = current_player
    return player

def request_hit(msg, client_id, player):
    game_status = game.cache.get_game_status()
    card, cards_deck = game.game_logic.hit(game_status.cards_deck)
    print("before 0", msg)
    player_new_bet = game.game_logic.bet(player=player, bet_value=int(msg["bet"]))
    game_status.cards_deck = cards_deck
    cards = player.cards
    for player in game_status.players:
        if player.player_id == client_id:
            player.cards = player.cards + [card]
            player.bet = player_new_bet.bet
    return game_status, cards + [card]

async def send_messages_about_other_players_hit(msg, client_id, cards):
    sending_msg = "The player {player_name} requested a hit, his cards are {cards}, and bet: {bet}".format(
        player_name=msg["player_name"], cards=cards, bet=msg["bet"]
    )
    message = {
            "type": "play",
            "your_turn": False,
            "content": sending_msg
    }
    for client in connected_clients.keys():
            await connected_clients[client].send(json.dumps(message))
    await playing_blackjack(client_id)
    
async def send_messages_about_other_players_stand(msg, client_id, cards):
    sending_msg = "The player {player_name} requested a stand, his cards are {cards}, and bet: {bet}".format(
        player_name=msg["player_name"], cards=cards, bet=msg["bet"]
    )
    message = json.dumps(
        {
            "type": "play",
            "your_turn": False,
            "content": sending_msg
        }
    )
    index_of_item = list(connected_clients.keys()).index(client_id)
    if index_of_item < len(list(connected_clients.keys())) - 1:
        index = index_of_item + 1
        
        for client in connected_clients.keys():
               await connected_clients[client].send(message)
                
        await playing_blackjack(list(connected_clients.keys())[index])
    else:
        await finish_game()
        
async def finish_game():
    game_status = game.dealer_round()
    sending_msg = "The dealer cards are {cards}".format(
        cards=game_status.dealer.cards
    )
    message = json.dumps(
        {
            "type": "dealer",
            "content": sending_msg
        }
    )
    await broadcast(message)
    
    message = {
        "type": "finish",
        "content": None
    }
    game_status = game.dealer_round()
    for player in game_status.players:
        if game.game_logic.sum_cards(player.cards) > game.game_logic.sum_cards(game_status.dealer.cards):
            sending_msg = "You beat the dealer, your card sum is {sum} and your credits is {credits}".format(
                sum=game.game_logic.sum_cards(player.cards), credits=player.credit
            )
            message["content"] = sending_msg
            await connected_clients[player.player_id].send(json.dumps(message))
        elif game.game_logic.sum_cards(player.cards) == game.game_logic.sum_cards(game_status.dealer.cards):
            sending_msg = "You draw with the dealer dealer, your card sum is {sum} and your credits is {credits}".format(
                sum=game.game_logic.sum_cards(player.cards), credits=player.credit
            )
            message["content"] = sending_msg
            await connected_clients[player.player_id].send(json.dumps(message))
        else:
            sending_msg = "You lose to the dealer, your card sum is {sum} and your credits is {credits}".format(
                sum=game.game_logic.sum_cards(player.cards), credits=player.credit
            )
            message["content"] = sending_msg
            await connected_clients[player.player_id].send(json.dumps(message))
    game.end_round()

async def game_run(websocket):
    async with connection_semaphore:
        client_id = str(uuid.uuid4())
        connected_clients[client_id] = websocket

        while True:
            try:
                async for message in websocket:
                    msg = json.loads(message)
                    if msg["type"] == "login" and game.cache.get_game_status().isRoundFinished == True:
                        game.cache.save_players_data(players= game.cache.load_players_data() + [
                            Player(
                                name=msg["name"],
                                player_id=msg["player_id"],
                                bet=0,
                                credit=100
                            )
                        ])
                        del connected_clients[client_id]
                        client_id = msg["player_id"]
                        connected_clients[client_id] = websocket
                        print("new user login: {player_id}".format(player_id=client_id))

                    if (msg["type"] == "play"):
                        
                        if msg["action"] == "hit":
                            player = get_player_with_id(player_id=msg["player_id"])
                            
                            game_status, cards = request_hit(msg, client_id, player)

                            #save player changes in cache
                            print(game_status.players)
                            game.cache.save_players_data(players=game_status.players)
                            game.cache.save_game_status(game=game_status)

                            # send messages to all players
                            await send_messages_about_other_players_hit(msg, client_id, cards)

                        if msg["action"] == "stand":
                            await send_messages_about_other_players_stand(msg, client_id, cards)
                                    
                    global first_time
                    if first_time:
                        first_time = False
                        await starting_game()
                        first_time = True

            except Exception as e:
                print(e)
                del connected_clients[client_id]

async def main():
    async with serve(game_run, WEBSOCKET_HOST, WEBSOCKET_PORT, ping_interval=None):
        print("server started")
        await asyncio.Future()  # run forever

asyncio.run(main())