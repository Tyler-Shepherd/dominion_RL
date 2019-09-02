import copy

class Player_State:
    def __init__(self, player):
        current_state = []
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
        # TODO fill this out, this is the import bit
        # every state is unique
        # but should order cards so that even if cards in hand, deck, discard, etc. are in different order still return same hash
        # probably don't need to serialize kingdom then

    def __hash__(self):
        # TODO fill out hash to match eq

        # try return 0 first and see what happens
        return 0