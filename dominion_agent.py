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

from player import Player
from card import Card

sys.path.append("./opponents")
from buy_only_treasure import Buy_Only_Treasure_Opponent

debug_mode = 0

class dominion_agent():
    def __init__(self):
        # Initialize learning model

        self.D_in = 5  # input dimension
        self.H = 3  # hidden dimension
        self.D_out = 1  # output dimension, just want q value

        self.model = torch.nn.Sequential(
            torch.nn.Linear(self.D_in, self.H),
            torch.nn.Sigmoid(),
            torch.nn.Linear(self.H, self.D_out)
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

        self.opponent = Buy_Only_Treasure_Opponent(self.kingdom)

        # Draw initial hand
        self.player.clean_up()

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
    Buys card a, has opponent play out turn then purchase, then plays out next turn for this player
    '''
    def make_move(self, a):
        if a is not None:
            if debug_mode >= 2:
                print("buying", a.name)

            self.player.hand.append(a)
            self.kingdom[a.id] -= 1

        self.player.clean_up()

        self.opponent.action_phase(debug_mode)
        self.opponent.buy_phase(debug_mode)

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