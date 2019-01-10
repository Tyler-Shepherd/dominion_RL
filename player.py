import random
from card import Card

# Abstract base class that describes a player
# Defines current state of deck, hand, and discard

class Player:

    def __init__(self):
        pass

    def reset_game(self):
        self.hand = []
        self.deck = [Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(3), Card(3), Card(3)]
        self.discard = []

        random.shuffle(self.deck)

        # draw first five
        self.clean_up()

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

    def action_phase(self):
        pass

    def buy_phase(self):
        pass

    '''
    Prints deck and hand
    '''
    def print_state(self):
        pdeck = []
        for card in self.deck:
            pdeck.append(card.name)
        print("Deck:", pdeck)

        phand = []
        for card in self.hand:
            phand.append(card.name)
        print("Hand:", phand)