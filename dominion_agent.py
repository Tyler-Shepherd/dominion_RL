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
import params as params

sys.path.append("./opponents")
from buy_only_treasure import Buy_Only_Treasure_Opponent

class dominion_agent():
    def __init__(self, loss_output_file):
        # Initialize learning model

        self.model = torch.nn.Sequential(
            torch.nn.Linear(params.D_in, params.H),
            torch.nn.Sigmoid(),
            torch.nn.Linear(params.H, params.D_out)
        )

        self.target_model = copy.deepcopy(self.model)
        for p in self.target_model.parameters():
            p.requires_grad = False
        self.target_model.load_state_dict(self.model.state_dict())

        self.running_loss = 0
        self.running_states = 0
        self.loss_output_file = loss_output_file

        self.loss_fn = torch.nn.MSELoss(size_average=False)  # using mean squared error

    '''
    Initializes environment for an iteration of learning
    env0 is the initial state of kingdom
    creates kingdom_0
    '''
    def initialize(self, env0):
        self.kingdom_0 = env0.copy()

    '''
    Resets game to beginning
    '''
    def reset_environment(self):
        self.kingdom = self.kingdom_0.copy()
        self.player = Player()
        self.trash = []
        self.turn_num = 1

        self.opponent = Buy_Only_Treasure_Opponent(self.kingdom)

        # Draw initial hand
        self.player.clean_up()
        self.opponent.player.clean_up()

        if params.debug_mode >= 3:
            print("Turn", self.turn_num)

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
            if self.kingdom[c] == 0 and self.kingdom_0[c] != 0:
                num_empty += 1

        if num_empty >= 3:
            return 2

        return -1

    '''
    Returns all possible cards purchaseable
    '''
    def get_legal_actions(self):
        coins = self.player.num_coins()
        if params.debug_mode >= 2:
            print("Agent has", coins, "coins")

        cards_purchasable = []

        # "skip" card
        cards_purchasable.append(Card(-1))

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
        # TODO: num remaining of each card in kingdom, num of each card in deck
        # num of each card opponent has, opponent vp total
        # player vp total
        # opponent - player vp difference
        # a's id
        # special for if a is Nothing?

        f = []
        f.append(self.player.num_coins())
        f.append(a.cost)
        f.append(2 * int(a.f_victory) - 1)
        f.append(2 * int(a.f_treasure) - 1)
        f.append(2 * int(a.f_action) - 1)
        f.append(self.turn_num)

        return Variable(torch.from_numpy(np.array(f)).float())

    def get_Q_val(self, a, use_target_net=False):
        state_features = self.state_features(a)

        if use_target_net:
            return self.target_model(state_features)
        return self.model(state_features)

    '''
    Buys card a, has opponent play out full turn, then plays out next turn's action phase for this player
    '''
    def make_move(self, a, f_testing = False):
        assert a is not None

        if params.debug_mode >= 2:
            print("Agent buying", a.name)

        # unless purchasing nothing, remove card from kingdom
        if a.id != -1:
            self.player.discard.append(a)
            self.kingdom[a.id] -= 1

        self.player.clean_up()

        self.opponent.action_phase()
        self.opponent.buy_phase()
        self.opponent.player.clean_up()

        # TODO what if the game ends here?

        self.turn_num += 1
        if params.debug_mode >= 3:
            print("Turn", self.turn_num)
        self.player.action_phase()

        if not f_testing:
            self.running_states += 1

            if self.running_states % params.print_loss_every == 0:
                print("*******LOSS:", self.running_loss / params.print_loss_every)
                self.loss_output_file.write(str(self.running_states) + '\t' + str(self.running_loss / params.print_loss_every) + '\n')
                self.loss_output_file.flush()

                self.running_loss = 0

    # Reward is the current difference in scores between player and opponent
    def reward(self):
        # current_state = self.at_goal_state()
        #
        # if current_state == -1:
        #     # Not a goal state
        #     reward_val =  0
        # else:
        #     reward_val = self.player.num_victory_points() - self.turn_num

        # doing this might incentive just buying estate early
        # could try doing this only when at end of game
        reward_val = self.player.num_victory_points() - self.opponent.player.num_victory_points()

        return torch.tensor(reward_val, dtype = torch.float32)

    def update_q(self, learning_rate, old_q_value, new_q_value):

        new_q_value = Variable(new_q_value)

        # Compute loss
        loss = self.loss_fn(old_q_value, new_q_value)

        self.running_loss += loss.item()

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

    '''
    Plays a single game on test_env
    Returns whether won, number of turns, number of VP of player, number of VP of opponent
    '''
    def test_model(self, test_env, test_output_full_file):
        self.initialize(test_env)
        self.reset_environment()

        test_output_full_file.write(str(test_env) + '\n')

        # Play using model greedily
        with torch.no_grad():
            while self.at_goal_state() == -1:
                legal_actions = self.get_legal_actions()

                max_action = None
                max_action_val = float("-inf")
                for e in legal_actions:
                    action_val = self.get_Q_val(e)

                    if action_val > max_action_val:
                        max_action = e
                        max_action_val = action_val

                test_output_full_file.write(str(self.turn_num) + '\t' + str(self.player.num_coins()) + '\t' + str(max_action.name) + '\n')

                self.make_move(max_action, f_testing=True)

        test_output_full_file.write('--------------------------------------------\n')

        player_vp = self.player.num_victory_points()
        opp_vp = self.opponent.player.num_victory_points()

        return player_vp > opp_vp, self.turn_num, player_vp, opp_vp

    def save_model(self, checkpoint_filename):
        torch.save(self.model.state_dict(), checkpoint_filename)
        print("Saved model to " + checkpoint_filename)

    def load_model(self, checkpoint_filename):
        checkpoint = torch.load(checkpoint_filename)
        self.model.load_state_dict(checkpoint)
        print("Loaded model from " + checkpoint_filename)