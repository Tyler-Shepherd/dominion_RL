import copy

import torch
import numpy as np
import random
from torch.autograd import Variable

from card import Card
from player import Player
from training import params as params
import dominion_utils

class Dominion_Agent(Player):
    def __init__(self, loss_output_file):
        super(Dominion_Agent, self).__init__("Training Agent")

        # Initialize learning model
        self.model = torch.nn.Sequential(
            torch.nn.Linear(params.D_in, params.H),
            torch.nn.ReLU(),
            torch.nn.Linear(params.H, params.H2),
            torch.nn.ReLU(),
            torch.nn.Linear(params.H2, params.D_out),
            torch.nn.ReLU()
        )

        self.target_model = copy.deepcopy(self.model)
        for p in self.target_model.parameters():
            p.requires_grad = False
        self.target_model.load_state_dict(self.model.state_dict())

        self.running_loss = 0
        self.loss_output_file = loss_output_file

        self.loss_fn = torch.nn.MSELoss(size_average=False)  # using mean squared error
        # self.loss_fn = torch.nn.SmoothL1Loss(size_average=False)  # Huber loss

    '''
    Returns all possible cards purchaseable
    '''
    def get_legal_actions(self):
        self.play_treasures()
        coins = self.coins

        cards_purchasable = dominion_utils.get_purchaseable_cards(self, coins, self.kingdom)

        return cards_purchasable

    def get_Q_val(self, a, use_target_net=False):
        state_features = dominion_utils.state_features(self, self.kingdom, a)

        if use_target_net:
            return self.target_model(state_features)
        return self.model(state_features)

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
    Does buy phase using learned model greedily
    '''
    def buy_phase(self):
        # list of (cost, bought card)
        purchases = []

        while self.num_buys > 0:
            legal_actions = self.get_legal_actions()

            max_action = None
            max_action_val = float("-inf")
            for e in legal_actions:
                action_val = self.get_Q_val(e)

                if params.debug_mode >= 3:
                    print(e.name, action_val.item())

                if action_val > max_action_val:
                    max_action = e
                    max_action_val = action_val

            assert max_action is not None

            # max_action = dominion_utils.force_buy(13, self, max_action)

            purchases.append((self.coins, max_action))
            dominion_utils.buy_card(self, max_action, self.kingdom)

        return purchases

    def action_phase(self):
        dominion_utils.generic_action_phase(self)

    def save_model(self, checkpoint_filename):
        torch.save(self.model.state_dict(), checkpoint_filename)
        print("Saved model to " + checkpoint_filename)

    def load_model(self, checkpoint_filename):
        checkpoint = torch.load(checkpoint_filename)
        self.model.load_state_dict(checkpoint)
        print("Loaded model from " + checkpoint_filename)

    def gain_card_up_to(self, limit):
        # todo use buy policy to choose which to gain
        # todo eventually make this its own policy? or at least update q values based on this choice
        # todo make this a dominion_util function we can call in both dominion_agent.py and agent.py

        gainable = dominion_utils.get_purchaseable_cards(self, limit, self.kingdom, True)
        card_to_gain = random.choice(gainable)
        dominion_utils.gain_card(self, card_to_gain, self.kingdom)

    def discard_down_to(self, handsize):
        # todo policy for this
        dominion_utils.generic_discard_down_to(self, handsize)