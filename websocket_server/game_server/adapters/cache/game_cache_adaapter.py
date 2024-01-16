import redis
import json
from game_server.entities.interfaces.game_cache_interface import GameCacheInterface
from typing import List
from game_server.entities.objects.player import Player
from game_server.entities.objects.game import Game
from game_server.entities.objects.dealer import Dealer
import os
name = "players"
game_name = "game_status"
port = os.getenv("REDIS_PORT")
host = os.getenv("REDIS_HOST")
password = os.getenv("REDIS_PASSWORD")

class GameCacheAdapter(GameCacheInterface):

    def __init__(self) -> None:
        self.redis = redis.Redis(host=host, port=port, decode_responses=True, password=password)

    def load_players_data(self):
        palyers = self.redis.get(name)
        loaded_data = json.loads(palyers)
        return [ self.get_player_as_obj(data) for data in loaded_data ]
    
    def get_player_as_obj(self, player):
        return Player(
            player_id = player["player_id"],
            name = player["name"],
            cards = player["cards"],
            bet = int(player["bet"]),
            credit = int(player["credit"]),
        )
    
    def get_palyer_as_dict(self, player):
        return {
            "player_id": player.player_id,
            "name": player.name,
            "cards": player.cards,
            "bet": player.bet,
            "credit": player.credit,
        }
    
    def save_players_data(self, players: List[Player]):
        data = [  self.get_palyer_as_dict(player)  for player in players ]
        serialized_data = json.dumps(data)
        self.redis.set(name, serialized_data)
    

    def get_game_as_dict(self, game: Game):
        return {
            "dealer": {
                "cards": game.dealer.cards
            },
            "cards_deck": game.cards_deck,
            "isRoundFinished": game.isRoundFinished,
            "isRoundStarting": game.isRoundStarting,
        }

    def get_game_as_obj(self, game):
        return Game(
            players = self.load_players_data(),
            dealer = Dealer(
                cards = game["dealer"]["cards"]
            ),
            cards_deck = game["cards_deck"],
            isRoundFinished = bool(game["isRoundFinished"]),
            isRoundStarting = bool(game["isRoundStarting"])
        )
    
    def get_game_status(self) -> Game:
        game_status = self.redis.get(game_name)
        loaded_data = json.loads(game_status)
        return self.get_game_as_obj(loaded_data)
    
    def save_game_status(self, game):
        data = self.get_game_as_dict(game)
        serialized_data = json.dumps(data)
        self.redis.set(game_name, serialized_data)