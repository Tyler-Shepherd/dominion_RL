from card import Card
import copy
import random
import training.params as params

class Kingdom:
    # Stores info about kingdom

    def __init__(self, supply):
        self.supply_initial = copy.deepcopy(supply)
        self.supply = copy.deepcopy(supply)
        self.trash = []
        self.turn_num = 0
        self.starting_player = 0

    def __str__(self):
        pkingdom = {}
        for card in self.supply.keys():
            pkingdom[Card(card).name] = self.supply[card]
        return str(pkingdom)

    def reset(self):
        self.supply = copy.deepcopy(self.supply_initial)
        self.trash = []
        self.turn_num = 0
        self.starting_player = 1 if random.random() < 0.5 else -1

    def next_turn(self):
        self.turn_num += 1
        if params.debug_mode >= 3:
            print("Turn", self.turn_num)

    def trash_card(self, card):
        self.trash.append(card)

    def buy_card(self, card):
        assert self.supply[card.id] > 0
        self.supply[card.id] -= 1

    def print_kingdom(self):
        pkingdom = {}
        for card in self.supply.keys():
            pkingdom[Card(card).name] = self.supply[card]
        print("Kingdom:", pkingdom)

    '''
    Returns -1 if not at goal state (game not over)
    Returns 1 if game is over (no provinces)
    Returns 2 if game is over (3 piles gone)
    '''
    def is_game_over(self):
        assert self.supply[5] >= 0
        if self.supply[5] == 0:
            if params.debug_mode >= 2:
                print("Game over - no Provinces")
            return 1

        num_empty = 0
        for c in self.supply.keys():
            if self.supply[c] == 0 and self.supply_initial[c] != 0:
                num_empty += 1

        if num_empty >= 3:
            if params.debug_mode >= 2:
                print("Game over - 3 piles empty")
            return 2

        return -1