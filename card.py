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
        self.f_attack = 0
        self.f_curse = 0

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
            # Curse
            self.f_curse = 1
            self.cost = 0
            self.victory_value = -1
            self.name = "Curse"
        elif id == 7:
            # Smithy
            self.f_action = 1
            self.cost = 4
            self.name = "Smithy"
        elif id == 8:
            # Village
            self.f_action = 1
            self.cost = 3
            self.name = "Village"
        elif id == 9:
            # Woodcutter
            self.f_action = 1
            self.cost = 3
            self.name = "Woodcutter"
        elif id == 10:
            # Witch
            self.f_action = 1
            self.f_attack = 1
            self.cost = 5
            self.name = "Witch"
        elif id == 11:
            # Moat
            self.f_action = 1
            self.f_reaction = 1
            self.cost = 2
            self.name = "Moat"
        elif id == 12:
            # Workshop
            self.f_action = 1
            self.cost = 3
            self.name = "Workshop"
        elif id == 13:
            # Council Room
            self.f_action = 1
            self.cost = 5
            self.name = "Council Room"
        elif id == 14:
            # Market
            self.f_action = 1
            self.cost = 5
            self.name = "Market"
        elif id == 15:
            # Harem
            self.f_treasure = 1
            self.f_victory = 1
            self.victory_value = 2
            self.coin_value = 2
            self.cost = 6
            self.name = "Harem"
        elif id == 16:
            # Militia
            self.f_action = 1
            self.f_attack = 1
            self.cost = 4
            self.name = "Militia"

    def play(self, player):
        assert self.f_action

        if params.debug_mode >= 2:
            print("Playing", self.name)

        # Trigger reactions if this is an Attack card
        opponent_unnaffected = player.opponent.attack_played() if self.f_attack else None

        if self.id == 7:
            # Smithy
            player.draw(3)
        elif self.id == 8:
            # Village
            player.draw(1)
            player.plus_actions(2)
        elif self.id == 9:
            # Woodcutter
            player.plus_buys(1)
            player.plus_coins(2)
        elif self.id == 10:
            # Witch
            player.draw(2)
            if not opponent_unnaffected:
                player.opponent.discard.append(Card(6))
        elif self.id == 11:
            # Moat
            player.draw(2)
        elif self.id == 12:
            # Workshop
            return player.gain_card_up_to(4)
        elif self.id == 13:
            # Council Room
            player.draw(4)
            player.plus_buys(1)
            player.opponent.draw(1)
        elif self.id == 14:
            # Market
            player.draw(1)
            player.plus_actions(1)
            player.plus_buys(1)
            player.plus_coins(1)
        elif self.id == 16:
            # Militia
            player.plus_coins(2)
            if not opponent_unnaffected:
                return player.opponent.discard_down_to(3)
        else:
            raise Exception('Unknown card id to be played')
