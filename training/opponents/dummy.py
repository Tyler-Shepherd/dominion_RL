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

        cards_purchasable = [Card(-1)]

        for c in self.kingdom.supply.keys():
            card = Card(c)
            if card.cost <= coins and self.kingdom.supply[c] > 0:
                cards_purchasable.append(card)

        if params.debug_mode >= 2:
            print("Opponent has", coins, "coins")

        bought_card = random.choice(cards_purchasable)
        dominion_utils.buy_card(self, bought_card, self.kingdom)

    def action_phase(self):
        action_cards = [card for card in self.hand if card.f_action]

        while self.num_actions > 0 and len(action_cards) > 0:
            # Currently just plays in order
            card_to_play = action_cards.pop()
            self.hand.remove(card_to_play)
            self.in_play.append(card_to_play)
            self.num_actions -= 1
            card_to_play.play(self)
            action_cards = [card for card in self.hand if card.f_action]

    def gain_card_up_to(self, limit):
        gainable = dominion_utils.get_purchaseable_cards(limit, self.kingdom)
        card_to_gain = random.choice(gainable)
        dominion_utils.gain_card(self, card_to_gain, self.kingdom)

    def discard_down_to(self, handsize):
        dominion_utils.generic_discard_down_to(self, handsize)