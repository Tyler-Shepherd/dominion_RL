from pprint import pprint
import random
import sys
import time
import math
import io
import os



# Card ids:
# 0 Copper
# 1 Silver
# 2 Gold
# 3 Estate
# 4 Duchy
# 5 Province
# 6 Smithy

# eventually want to have this all stored in a database of some sort

class Card:
    # Stores attributes of a card

    def __init__(self, id):
        self.id = id

        self.f_treasure = 0
        self.f_victory = 0
        self.f_action = 0

        self.coin_value = 0
        self.victory_value = 0

        self.cost = 0

        self.name = ""

        if id == 0:
            # Copper
            self.f_treasure = 1
            self.coin_value = 1
            self.name = "Copper"
        elif id == 1:
            # Silver
            self.f_treasure = 1
            self.coin_value = 2
            self.cost = 3
            self.name = "Silver"
        elif id == 2:
            # Gold
            self.f_treasure = 1
            self.coin_value = 3
            self.cost = 6
            self.name = "Gold"
        elif id == 3:
            # Estate
            self.f_victory = 1
            self.victory_value = 1
            self.cost = 2
            self.name = "Estate"
        elif id == 4:
            # Duchy
            self.f_victory = 1
            self.victory_value = 3
            self.cost = 5
            self.name = "Duchy"
        elif id == 5:
            # Province
            self.f_victory = 1
            self.victory_value = 6
            self.cost = 8
            self.name = "Province"
        elif id == 6:
            # Smithy
            self.f_action = 1
            self.cost = 4
            self.name = "Smithy"

    def play(self, player):
        print("playing " + self.name)
        if self.id == 6:
            # Smithy
            player.draw(3)
            print_hand(player)


class Player:
    # Stores current state of player

    def __init__(self):
        self.hand = []
        self.deck = [Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(3), Card(3), Card(3)]
        self.discard = []

        random.shuffle(self.deck)

    def draw(self, num_to_draw):
        cards_drawn = []

        for i in range(num_to_draw):
            if not self.deck:
                # If deck empty, reshuffle
                print("...reshuffle...")
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



    def buy_phase(self):
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






def goal_state():
    if kingdom[5] == 0:
        return True

    # also need to include "any 3 are 0"

    return False


def print_deck(player):
    pdeck = []

    for card in player.deck:
        pdeck.append(card.name)

    print("Deck:", pdeck)

def print_hand(player):
    phand = []

    for card in player.hand:
        phand.append(card.name)

    print("Hand:", phand)

def print_cards(cards):
    pcards = []

    for card in cards:
        pcards.append(card.name)

    print(pcards)

# Stores current state of kingdom as card_id -> num in pile
kingdom = {}
trash = []


# Q learning parameters
learning_rate = 0.04
discount_factor = 0.8
exploration_rate = 0.4

num_iterations = 100

# Stores tuples (kingdom, card_id) to q value
# This is at a kingdom state and purchasing card
Q = {}



if __name__ == '__main__':
    # Initialize kingdom

    kingdom_0 = {0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}


    for iter in range(num_iterations):
        # Reset environment (kingdom and player)
        player1 = Player()
        player1.clean_up()

        kingdom = kingdom_0.copy()
        trash = []

        turn_num = 1

        while not goal_state():
            print(" ")
            print("turn", turn_num)
            print(kingdom)
            print_hand(player1)
            print_deck(player1)

            player1.action_phase()

            player1.buy_phase()

            player1.clean_up()

            turn_num += 1
