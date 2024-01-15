from dataclasses import dataclass
from game_server.entities.objects.player import Player
from game_server.entities.objects.dealer import Dealer
from typing import List

@dataclass
class Game:
    players: List[Player]
    dealer: Dealer
    cards_deck: List[str]
    isRoundFinished: bool
    isRoundStarting: bool