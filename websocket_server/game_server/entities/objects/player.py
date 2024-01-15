from dataclasses import dataclass
from typing import List

@dataclass
class Player:
    player_id: str = None
    name: str = None
    cards: List[str] = None
    bet: int = None
    credit: int = None