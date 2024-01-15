import abc
from game_server.entities.objects.player import Player
from game_server.entities.objects.game import Game
from typing import List

class GameCacheInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_players_data(self) -> List[Player]:
        """Return players info"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def save_players_data(self, players: List[Player]):
        """Save players info"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_game_status(self) -> Game:
        """Get game status"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def save_game_status(self, game: Game):
        """Save game status"""
        raise NotImplementedError