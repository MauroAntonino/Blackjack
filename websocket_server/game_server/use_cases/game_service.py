from game_server.entities.interfaces.game_logic_interface import GameLogicInterface
from game_server.entities.interfaces.game_cache_interface import GameCacheInterface
from game_server.entities.objects.game import Game
from game_server.entities.objects.player import Player
from game_server.entities.objects.dealer import Dealer

class GameService:

    def __init__(self, logic: GameLogicInterface, cache: GameCacheInterface) -> None:
        self.game_logic :GameLogicInterface = logic
        self.cache :GameLogicInterface = cache
    
    def load_game(self) -> Game:
        game_status = Game(
            players=self.cache.load_players_data(),
            dealer=Dealer(),
            cards_deck=self.game_logic.shuffle_cards(),
            isRoundStarting=False,
            isRoundFinished=False
        )
        self.cache.save_players_data(players=game_status.players)
        self.cache.save_game_status(game=game_status)

    def get_cards(self):
        game = self.cache.get_game_status()
        game_status = self.game_logic.get_dealer_and_player_first_cards(
            game_status=game,
            cards_deck=self.game_logic.shuffle_cards()
        )
        self.cache.save_players_data(players=game_status.players)
        self.cache.save_game_status(game=game_status)
    
    def dealer_round(self):
        game_status = self.cache.get_game_status()
        while self.game_logic.sum_cards(game_status.dealer.cards) < 17:
            card, cards_deck = self.game_logic.hit(game_status.cards_deck)
            game_status.dealer.cards += card
            game_status.cards_deck = cards_deck
        self.cache.save_players_data(players=game_status.players)
        self.cache.save_game_status(game=game_status)
        return game_status
    
    def end_round(self):
        game_status = self.cache.get_game_status()
        game_status = self.game_logic.end_round(game_status=game_status)
        self.cache.save_players_data(players=game_status.players)
        self.cache.save_game_status(game=game_status)
        return game_status
        
