import copy

import torch
import numpy as np
from torch.autograd import Variable

from card import Card
from player import Player
from training import params as params
import dominion_utils

class Dominion_Agent(Player):
    def __init__(self, loss_output_file):
        super(Dominion_Agent, self).__init__()

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
        self.loss_output_file = loss_output_file

        # self.loss_fn = torch.nn.MSELoss(size_average=False)  # using mean squared error
        self.loss_fn = torch.nn.SmoothL1Loss(size_average=False)  # Huber loss

    '''
    Returns all possible cards purchaseable
    '''
    def get_legal_actions(self):
        self.play_treasures()
        coins = self.coins
        if params.debug_mode >= 2:
            print("Agent has", coins, "coins")

        cards_purchasable = []

        # "skip" card
        cards_purchasable.append(Card(-1))

        for c in self.kingdom.supply.keys():
            card = Card(c)
            if card.cost <= coins and self.kingdom.supply[c] > 0:
                cards_purchasable.append(card)

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
        dominion_utils.buy_card(self, max_action, self.kingdom)

        if params.debug_mode >= 2:
            print("Agent buying", max_action.name)

        # should return list of cards when multiple buys
        return max_action

    def action_phase(self):
        actions_remaining = 1
        action_cards = [card for card in self.hand if card.f_action]

        while actions_remaining > 0 and len(action_cards) > 0:
            # Currently just plays in order
            card_to_play = action_cards.pop()
            self.hand.remove(card_to_play)
            self.in_play.append(card_to_play)
            card_to_play.play(self)
            actions_remaining -= 1

    def save_model(self, checkpoint_filename):
        torch.save(self.model.state_dict(), checkpoint_filename)
        print("Saved model to " + checkpoint_filename)

    def load_model(self, checkpoint_filename):
        checkpoint = torch.load(checkpoint_filename)
        self.model.load_state_dict(checkpoint)
        print("Loaded model from " + checkpoint_filename)

