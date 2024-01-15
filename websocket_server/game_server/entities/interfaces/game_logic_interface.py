import abc
from typing import List
from game_server.entities.objects.game import Game

class GameLogicInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def shuffle_cards(self) -> List[str]:
        """shuffle cards"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_dealer_and_player_first_cards(self, game_status: Game, cards_deck: List[str]) -> Game:
        """get cards"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def hit(self, cards_deck: List[str]) -> str:
        """hit"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def end_round(self, game_status: Game) -> Game:
        """end_round"""
        raise NotImplementedError