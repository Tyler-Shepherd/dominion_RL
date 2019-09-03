import copy
import dominion_utils

class Player_State:
    def __init__(self, player):
        self.hand = player.hand.copy()
        self.deck = player.deck.copy()
        self.discard = player.discard.copy()
        self.in_play = player.in_play.copy()
        self.opponent_hand = player.opponent.hand.copy()
        self.opponent_deck = player.opponent.deck.copy()
        self.opponent_discard = player.opponent.discard.copy()
        self.kingdom = copy.deepcopy(player.kingdom)
        self.num_actions = player.num_actions
        self.num_buys = player.num_buys
        self.coins = player.coins

    def __eq__(self, other):
        self_all = self.hand.copy()
        self_all.extend(self.deck)
        self_all.extend(self.discard)
        self_all.extend(self.in_play)

        other_all = other.hand.copy()
        other_all.extend(other.deck)
        other_all.extend(other.discard)
        other_all.extend(other.in_play)

        return \
            dominion_utils.cards_equivalent(self_all, other_all) \
            and self.kingdom == other.kingdom \
            and self.num_buys == other.num_buys \
            and self.coins == other.coins

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # this does work, since python always does equality check as well
        # but just leads to terrible performance
        return 0