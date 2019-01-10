import random

from card import Card
from training import params as params
from player import Player

# Describes a live person
# Gets actions and purchases updated live from flask app
# TODO

class Person(Player):

    def __init__(self):
        assert 1 == 2
        super(Person, self).__init__()

    def draw(self, num_to_draw):
        cards_drawn = []

        for i in range(num_to_draw):
            if not self.deck:
                # If deck empty, reshuffle
                random.shuffle(self.discard)
                self.deck += self.discard
                self.discard = []

            if self.deck:
                to_draw = self.deck.pop()
                self.hand.append(to_draw)
                cards_drawn.append(to_draw)

        return cards_drawn

    def clean_up(self):
        self.discard += self.hand
        self.hand = []
        self.draw(5)


    def action_phase(self):
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

    def num_coins(self):
        coins = sum(card.coin_value for card in self.hand if card.f_treasure)
        return coins

    '''
    Returns num victory points in entire deck
    '''
    def num_victory_points(self):
        vp_deck = sum(card.victory_value for card in self.deck if card.f_victory)
        vp_discard = sum(card.victory_value for card in self.discard if card.f_victory)
        vp_hand = sum(card.victory_value for card in self.hand if card.f_victory)

        return vp_deck + vp_discard + vp_hand

    # def buy_phase(self):
    #     coins = sum(card.coin_value for card in self.hand if card.f_treasure)
    #
    #     print("has", coins, "coins")
    #
    #     card_to_buy = None
    #     max_cost = -1
    #     for c in kingdom.keys():
    #         card = Card(c)
    #         if card.cost > max_cost and card.cost <= coins and kingdom[c] > 0:
    #             card_to_buy = card
    #             max_cost = Card(c).cost
    #
    #     print("buying", card_to_buy.name)
    #
    #     if card_to_buy is not None:
    #         self.hand.append(card_to_buy)
    #         kingdom[card_to_buy.id] -= 1
