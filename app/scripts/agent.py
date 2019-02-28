import random

from card import Card
from training import params as params
from player import Player
import dominion_utils

import torch
import numpy as np
from torch.autograd import Variable

# Describes an agent to play against
# Gets actions and purchases from RL model

class Agent(Player):

    def __init__(self):
        super(Agent, self).__init__()

    def initialize(self, kingdom):
        self.kingdom = kingdom

        # Initialize learning model
        self.model = torch.nn.Sequential(
            torch.nn.Linear(params.D_in, params.H),
            torch.nn.Sigmoid(),
            torch.nn.Linear(params.H, params.D_out)
        )

        checkpoint = torch.load(params.checkpoint_filename)
        self.model.load_state_dict(checkpoint)
        print("Loaded model from " + params.checkpoint_filename)

    def action_phase(self):
        pass

    def buy_phase(self):
        self.play_treasures()

        purchaseable_cards = dominion_utils.get_purchaseable_cards(self.coins, self.kingdom)
        print("Agent purchaseable:", dominion_utils.cards_to_string(purchaseable_cards))

        max_action = None
        max_action_val = float("-inf")

        for e in purchaseable_cards:
            state_features = dominion_utils.state_features(self, self.kingdom, e)
            action_val = self.model(state_features)

            print(e.name, action_val.item())

            if action_val > max_action_val:
                max_action = e
                max_action_val = action_val

        assert max_action is not None

        print("Agent buying", max_action.name)

        dominion_utils.buy_card(self, max_action, self.kingdom)

        return max_action

