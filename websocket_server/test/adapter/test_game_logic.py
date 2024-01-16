import unittest
from game_server.adapters.logic.game_logic_adapter import GameLogicAdapter
from game_server.entities.objects.player import Player

game_logic = GameLogicAdapter()

class TestGameLogic(unittest.TestCase):

    def test_shuffle_cards_give_different_results(self):
        cards = game_logic.shuffle_cards()
        cards_2 = game_logic.shuffle_cards()
        self.assertTrue(cards != cards_2)
    
    def test_shuffle_cards_len_is_52(self):
        cards = game_logic.shuffle_cards()
        self.assertTrue(len(cards) == 52)

    def test_bet(self):
        player = Player(
            name="test",
            bet = 10,
            credit = 100
        )
        bet_value = 20
        
        updated_player: Player = game_logic.bet(player=player, bet_value=bet_value)
        
        self.assertTrue(updated_player.bet == 30)
        self.assertTrue(updated_player.credit == 80)
        
    def test_hit(self):
        cards_deck = ["J", "1", "10"]
        
        card, cards_deck = game_logic.hit(cards_deck=cards_deck) 
        
        self.assertTrue(card == "J")
        self.assertTrue(cards_deck == ["1", "10"])


if __name__ == '__main__':
    unittest.main()