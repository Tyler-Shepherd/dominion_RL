import random
import copy
from card import Card
import training.params as params
import dominion_utils
from player_state import Player_State

# Abstract base class that describes a player
# Defines current state of deck, hand, and discard

class Player:

    def __init__(self, name):
        self.opponent = None
        self.name = name
        pass

    '''
    Initializes environment for an iteration of learning
    '''
    def initialize(self, kingdom):
        self.kingdom = kingdom

    def reset_game(self):
        self.hand = []
        self.deck = [Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(0), Card(3), Card(3), Card(3)]
        self.discard = []
        self.in_play = []
        self.coins = 0
        self.num_actions = 1
        self.num_buys = 1

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

        if params.debug_mode == 3:
            print(self.name, "drew", dominion_utils.cards_to_string(cards_drawn))

        return cards_drawn

    def plus_actions(self, num_actions):
        self.num_actions += num_actions

    def plus_coins(self, num_coins):
        self.coins += num_coins

    def plus_buys(self, num_buys):
        self.num_buys += num_buys

    def clean_up(self):
        self.discard += self.hand
        self.discard += self.in_play
        self.hand = []
        self.in_play = []
        self.coins = 0
        self.draw(5)
        self.num_actions = 1
        self.num_buys = 1

    def play_treasures(self):
        for card in self.hand:
            if card.f_treasure:
                self.coins += card.coin_value
                self.in_play.append(card)
        self.hand = [c for c in self.hand if not c.f_treasure]

    '''
    Returns num victory points in entire deck
    '''
    def num_victory_points(self):
        vp_deck = sum(card.victory_value for card in self.deck if (card.f_victory or card.f_curse))
        vp_discard = sum(card.victory_value for card in self.discard if (card.f_victory or card.f_curse))
        vp_hand = sum(card.victory_value for card in self.hand if (card.f_victory or card.f_curse))

        return vp_deck + vp_discard + vp_hand

    def action_phase(self):
        assert 1==2 # this shouldn't be called, should be implemented in child classes
        pass

    def buy_phase(self):
        assert 1==2 # this shouldn't be called, should be implemented in child classes
        pass

    '''
    Prints deck and hand
    '''
    def print_state(self):
        print("State for ", self.name)

        pinplay = []
        for card in self.in_play:
            pinplay.append(card.name)
        print("In Play:", pinplay)

        pdeck = []
        for card in self.deck:
            pdeck.append(card.name)
        print("Deck:", pdeck)

        phand = []
        for card in self.hand:
            phand.append(card.name)
        print("Hand:", phand)

        pdiscard = []
        for card in self.discard:
            pdiscard.append(card.name)
        print("Discard:", pdiscard)

    def get_state(self):
        # state is of form [hand, deck, discard, in play, opp hand, opp deck, opp discard, kingdom, num_actions]
        return Player_State(self)

    def set_state(self, new_state):
        # Note: you can't set state and then continue playing an actual game since opponent won't have Kingdom updated (maybe????)
        # Only used for getting and updating q values
        self.hand = new_state.hand
        self.deck = new_state.deck
        self.discard = new_state.discard
        self.in_play = new_state.in_play
        self.opponent.hand = new_state.opponent_hand
        self.opponent.deck = new_state.opponent_deck
        self.opponent.discard = new_state.opponent_discard
        self.kingdom = new_state.kingdom
        self.num_actions = new_state.num_actions
        self.num_buys = new_state.num_buys
        self.coins = new_state.coins

    def attack_played(self):
        # TODO give choice of playing reactions (especially in app)
        if any(card.id == 11 for card in self.hand):
            if params.debug_mode >= 2:
                print("Moat revealed - Attack blocked")
            return True

        return False

    def gain_card_up_to(self, limit):
        assert 1==2 # this shouldn't be called, should be implemented in child classes
        pass

    def discard_down_to(self, handsize):
        assert 1==2 # this shouldn't be called, should be implemented in child classes
        pass