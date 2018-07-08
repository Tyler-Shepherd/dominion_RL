from player import Player
from card import Card

class Buy_Only_Treasure_Opponent:
    def __init__(self, kingdom):
        self.player = Player()
        self.kingdom = kingdom # hope this changes with other player


    def buy_phase(self, debug_mode):
        coins = self.player.num_coins()

        cards_purchasable = []

        for c in self.kingdom.keys():
            card = Card(c)
            if card.cost <= coins and self.kingdom[c] > 0:
                cards_purchasable.append(card)

        if coins >= 8:
            self.player.hand.append(Card(5))
            self.kingdom[5] -= 1
            if debug_mode >= 2:
                print("Opponent purchasing Province")
        elif coins >= 6 and self.kingdom[2] > 0:
            self.player.hand.append(Card(2))
            self.kingdom[2] -= 1
            if debug_mode >= 2:
                print("Opponent purchasing Gold")
        elif coins >= 3 and self.kingdom[1] > 0:
            self.player.hand.append(Card(1))
            self.kingdom[1] -= 1
            if debug_mode >= 2:
                print("Opponent purchasing Silver")
        elif debug_mode >= 2:
            print("Opponent purchasing nothing")

        self.player.clean_up()



    def action_phase(self, debug_mode):
        pass