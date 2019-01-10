import random

from card import Card
from training import params as params
from player import Player

# Describes an agent
# Gets actions and purchases from learned model
# Used only in flask app
# TODO

class Agent(Player):

    def __init__(self):
        assert 1==2
        super(Agent, self).__init__()

    def action_phase(self):
        # TODO
        actions_remaining = 1

        action_cards = [card for card in self.hand if card.f_action]

        while actions_remaining > 0 and len(action_cards) > 0:
            # Currently just plays in order
            card_to_play = action_cards.pop()
            self.hand.remove(card_to_play)
            card_to_play.play(self)
            actions_remaining -= 1

            if params.debug_mode >= 2:
                print("Playing", card_to_play.name)

    def buy_phase(self):
        # TODO
        coins = sum(card.coin_value for card in self.hand if card.f_treasure)

        print("has", coins, "coins")

        card_to_buy = None
        max_cost = -1
        for c in kingdom.keys():
            card = Card(c)
            if card.cost > max_cost and card.cost <= coins and kingdom[c] > 0:
                card_to_buy = card
                max_cost = Card(c).cost

        print("buying", card_to_buy.name)

        if card_to_buy is not None:
            self.hand.append(card_to_buy)
            kingdom[card_to_buy.id] -= 1
