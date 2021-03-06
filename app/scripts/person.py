import random

from card import Card
from training import params as params
from player import Player
from follow_up import Follow_Up

# Describes a live person
# Gets actions and purchases updated live from flask app

class Person(Player):

    def __init__(self):
        super(Person, self).__init__("Person")

    def initialize(self, kingdom):
        self.kingdom = kingdom

    def action_phase(self):
        pass

    def buy_phase(self):
        pass

    def gain_card_up_to(self, limit):
        return Follow_Up(1, self, {"gain_card_limit": limit})

    def discard_down_to(self, handsize):
        return Follow_Up(2, self, {"handsize": handsize})