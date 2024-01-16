from game_server.entities.interfaces.game_logic_interface import GameLogicInterface
from game_server.entities.objects.game import Game
from game_server.entities.objects.player import Player
from typing import List
import random

class GameLogicAdapter(GameLogicInterface):

    def shuffle_cards(self) -> List[str]:
        cards_deck = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] * 4
        random.shuffle(cards_deck)
        return cards_deck
    
    def get_dealer_and_player_first_cards(self, game_status: Game, cards_deck: List[str]) -> Game:
        game_status.dealer.cards = cards_deck[:2]
        cards_deck = cards_deck[2:]
        for player in game_status.players:
            player.cards = cards_deck[:1]
            cards_deck = cards_deck[1:]
        game_status.cards_deck = cards_deck
        return game_status
    
    def hit(self, cards_deck: List[str]) -> str:
        card = cards_deck[0]
        cards_deck = cards_deck[1:]
        return card, cards_deck
    
    def bet(self, player: Player, bet_value: int) -> str:
        player.bet += bet_value
        player.credit -= bet_value
        return player
    
    def end_round(self, game_status: Game) -> Game:
        for player in game_status.players:
            sum_dealer = self.sum_cards(game_status.dealer.cards)
            sum_player = self.sum_cards(player.cards)
            if sum_dealer == sum_player and sum_player <= 21:
                player.credit += player.bet
            if sum_dealer < sum_player and sum_player <= 21:
                player.credit += player.bet * 2
            if sum_dealer > 21 and sum_player <= 21:
                player.credit += player.bet * 2
        game_status.isRoundFinished = True
        return game_status
    
    def convert_card_to_number(self, card):
        if card in ["J", "Q", "K"]:
            return 10
        if card == 1:
            return 11
        return int(card)

    def sum_cards(self, cards: List[str]):
        cards = list(map(self.convert_card_to_number, cards))
        total = sum(cards)
        num_as = cards.count("1")

        while total > 21 and num_as:
            total -= 10
            num_as -= 1
        
        return total
    
    
