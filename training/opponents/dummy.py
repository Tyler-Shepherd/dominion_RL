from card import Card
from player import Player
from training import params as params
import random

import dominion_utils

class Dummy_Opponent(Player):
    def __init__(self):
        super(Dummy_Opponent, self).__init__("Dummy Opponent")

    def buy_phase(self):
        self.play_treasures()
        coins = self.coins

        cards_purchasable = dominion_utils.get_purchaseable_cards(self, coins, self.kingdom)

        bought_card = random.choice(cards_purchasable)
        dominion_utils.buy_card(self, bought_card, self.kingdom)

    def action_phase(self):
        dominion_utils.generic_action_phase(self)

    def gain_card_up_to(self, limit):
        gainable = dominion_utils.get_purchaseable_cards(self, limit, self.kingdom, True)
        card_to_gain = random.choice(gainable)
        dominion_utils.gain_card(self, card_to_gain, self.kingdom)

    def discard_down_to(self, handsize):
        dominion_utils.generic_discard_down_to(self, handsize)