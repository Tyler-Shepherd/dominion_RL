import training.params as params

# Card ids:
# 0 Copper
# 1 Silver
# 2 Gold
# 3 Estate
# 4 Duchy
# 5 Province
# 6 Smithy

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

        if id == -1:
            # Special "skip buy" card
            self.name = "Nothing"
        elif id == 0:
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
        elif id == 7:
            # Village
            self.f_action = 1
            self.cost = 3
            self.name = "Village"

    def play(self, player):
        if params.debug_mode >= 2:
            print("Playing", self.name)

        if self.id == 6:
            # Smithy
            player.draw(3)
        elif self.id == 7:
            # Village
            player.plus_actions(2)
            player.draw(1)
