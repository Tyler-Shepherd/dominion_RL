from player import Player
from card import Card

import params as params

class Buy_Only_Treasure_Opponent:
    def __init__(self, kingdom):
        self.player = Player()
        self.kingdom = kingdom # hope this changes with other player


    def buy_phase(self):
        coins = self.player.num_coins()

        cards_purchasable = []

        for c in self.kingdom.keys():
            card = Card(c)
            if card.cost <= coins and self.kingdom[c] > 0:
                cards_purchasable.append(card)

        if params.debug_mode >= 2:
            print("Opponent has", coins, "coins")

        if coins >= 8:
            self.player.hand.append(Card(5))
            self.kingdom[5] -= 1
            if params.debug_mode >= 2:
                print("Opponent purchasing Province")
        elif coins >= 6 and self.kingdom[2] > 0:
            self.player.hand.append(Card(2))
            self.kingdom[2] -= 1
            if params.debug_mode >= 2:
                print("Opponent purchasing Gold")
        elif coins >= 3 and self.kingdom[1] > 0:
            self.player.hand.append(Card(1))
            self.kingdom[1] -= 1
            if params.debug_mode >= 2:
                print("Opponent purchasing Silver")
        elif params.debug_mode >= 2:
            print("Opponent purchasing Nothing")



    def action_phase(self):
        pass