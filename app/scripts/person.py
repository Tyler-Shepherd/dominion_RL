import random

from card import Card
from training import params as params
from player import Player

# Describes a live person
# Gets actions and purchases updated live from flask app

class Person(Player):

    def __init__(self):
        super(Person, self).__init__()

    def initialize(self, kingdom):
        self.kingdom = kingdom

    def action_phase(self):
        pass

    def buy_phase(self):
        pass
