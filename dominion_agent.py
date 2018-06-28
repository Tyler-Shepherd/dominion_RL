import io
import os
import math
import time
import numpy as np
from numpy import *
from numpy import linalg as LA
import itertools
from profile import Profile
import copy
import sys
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from queue import PriorityQueue
import torch
from torch.autograd import Variable
import random
from pprint import pprint
import glob

debug_mode = 0

# Card ids:
# 0 Copper
# 1 Silver
# 2 Gold
# 3 Estate
# 4 Duchy
# 5 Province
# 6 Smithy

# eventually want to have this all stored in a database

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
        if debug_mode >= 3:
            print("playing " + self.name)
        if self.id == 6:
            # Smithy
            player.draw(3)


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
                if debug_mode >= 3:
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



class dominion_agent():
    def __init__(self):
        # Initialize learning model

        D_in = 5  # input dimension
        H = 3  # hidden dimension
        D_out = 1  # output dimension, just want q value

        self.model = torch.nn.Sequential(
            torch.nn.Linear(D_in, H),
            torch.nn.Sigmoid(),
            torch.nn.Linear(H, D_out)
        )

        self.loss_fn = torch.nn.MSELoss(size_average=False)  # using mean squared error

        self.turn_num = 1

    '''
    Initializes environment for an iteration of learning
    env0 is the initial state of kingdom
    creates kingdom_0
    '''
    def initialize(self, env0):
        self.kingdom_0 = env0.copy()
        self.turn_num = 1

    '''
    Resets G (the current RP graph), E (the graph of unadded edges) and K (the known winners)
    '''
    def reset_environment(self):
        self.kingdom = self.kingdom_0.copy()
        self.player = Player()
        self.trash = []
        self.turn_num = 1

    '''
    Returns -1 if not at goal state (game not over)
    Returns 1 if game is over (no provinces)
    Returns 2 if game is over (3 piles gone)
    '''
    def at_goal_state(self):
        if self.kingdom[5] == 0:
            return 1

        num_empty = 0
        for c in self.kingdom.keys():
            if self.kingdom[c] == 0:
                num_empty += 1

        if num_empty >= 3:
            return 2

        return -1

    '''
    Returns all possible cards purchaseable
    '''
    def get_legal_actions(self):
        coins = self.player.num_coins()
        if debug_mode >= 2:
            print("has", coins, "coins")

        cards_purchasable = []

        for c in self.kingdom.keys():
            card = Card(c)
            if card.cost <= coins and self.kingdom[c] > 0:
                cards_purchasable.append(card)

        return cards_purchasable

    '''
    Prints deck and hand
    '''
    def print_state(self):
        pdeck = []
        for card in self.player.deck:
            pdeck.append(card.name)
        print("Deck:", pdeck)

        phand = []
        for card in self.player.hand:
            phand.append(card.name)
        print("Hand:", phand)

        pkingdom = {}
        for card in self.kingdom.keys():
            pkingdom[Card(card).name] = self.kingdom[card]
        print("Kingdom:", pkingdom)

    # Returns input layer features at current state buying Card a
    def state_features(self, a):
        # ideas: num remaining of each card in kingdom, num of each card in deck

        f = []
        f.append(self.player.num_coins())
        f.append(a.cost)
        f.append(2 * int(a.f_victory) - 1)
        f.append(2 * int(a.f_treasure) - 1)
        f.append(2 * int(a.f_action) - 1)

        # for c in self.kingdom.keys():
        #     f.append(self.kingdom[c])

        return Variable(torch.from_numpy(np.array(f)).float())

    def get_Q_val(self, a):
        state_features = self.state_features(a)
        return self.model(state_features)

    # Doesn't need to do anything
    def goal_state_update(self):
        pass

    def print_model(self, output_file):
        for p in self.model.parameters():
            print(p)

    '''
    Buys card a then plays out next turn
    '''
    def make_move(self, a):
        if a is not None:
            if debug_mode >= 2:
                print("buying", a.name)

            self.player.hand.append(a)
            self.kingdom[a.id] -= 1

        self.player.clean_up()

        self.turn_num += 1
        if debug_mode >= 3:
            print("Turn", self.turn_num)
        self.player.action_phase()

    # num victory points owned or num turns in?
    def reward(self):

        current_state = self.at_goal_state()

        if current_state == -1:
            # Not a goal state
            reward_val =  0
        else:
            reward_val = self.player.num_victory_points() - self.turn_num

        return torch.tensor(reward_val, dtype = torch.float32)

    def update_q(self, learning_rate, old_q_value, new_q_value):

        new_q_value = Variable(new_q_value)

        # Compute loss
        loss = self.loss_fn(old_q_value, new_q_value)

        # Zero the gradients before running the backward pass.
        self.model.zero_grad()

        # Backward pass: compute gradient of the loss with respect to all the learnable
        # parameters of the model. Internally, the parameters of each Module are stored
        # in Tensors with requires_grad=True, so this call will compute gradients for
        # all learnable parameters in the model.
        loss.backward()

        # Update the weights using gradient descent. Each parameter is a Tensor
        with torch.no_grad():
            for param in self.model.parameters():
                param -= learning_rate * param.grad

    # Play num_iterations games on kingdom test_env, record num turns to win
    def test_model(self, test_env):
        # Save the model
        torch.save(self.model.state_dict(), "checkpoint.pth.tar")

        self.initialize(test_env)

        # Play using model greedily
        self.reset_environment()

        while self.at_goal_state() == -1:
            legal_actions = self.get_legal_actions()

            max_action = None
            max_action_val = float("-inf")
            for e in legal_actions:
                action_val = self.get_Q_val(e)

                if action_val > max_action_val:
                    max_action = e
                    max_action_val = action_val

            self.make_move(max_action)

        return self.turn_num, self.player.num_victory_points()

    def load_model(self, checkpoint_filename):
        checkpoint = torch.load(checkpoint_filename)
        self.model.load_state_dict(checkpoint)