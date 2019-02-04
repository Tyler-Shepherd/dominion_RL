import random

from card import Card
from training import params as params
from player import Player

# Describes an agent to play against
# Gets actions and purchases from RL model

class Agent(Player):

    def __init__(self):
        super(Agent, self).__init__()

    def initialize(self, kingdom):
        self.kingdom = kingdom

    def action_phase(self):
        pass

    def buy_phase(self):
        pass
