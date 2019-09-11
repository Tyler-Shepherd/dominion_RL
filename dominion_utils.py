import numpy as np
import random
import torch
from torch.autograd import Variable

import training.params as params
from card import Card
from kingdom import Kingdom

def buy_card(player, card, kingdom):
    assert player.num_buys > 0
    player.num_buys -= 1
    if params.debug_mode >= 3:
        print(player.name, "buying", card.name)
    if card.id != -1:
        assert player.coins >= card.cost
        player.coins -= card.cost
        gain_card(player, card, kingdom)

def gain_card(player, card, kingdom):
    if params.debug_mode >= 3:
        print(player.name, "gaining", card.name)
    if card.id != -1:
        kingdom.gain_card(card)
        player.discard.append(card)

# Prints the total sum of weights off each input feature
def print_feature_weights(model_full):
    # Print weights
    model = model_full.parameters()

    is_bias = -1

    weights = []

    sum_weights_from_node_to_output = []

    # collect all the weights
    for p in model:
        if is_bias == -1:
            prev_layer_len = len(p[0])
            next_layer_len = len(p)
            layer_weights = np.zeros((prev_layer_len, next_layer_len))

            for i in range(next_layer_len):
                weights_to_i = p[i]
                for j in range(prev_layer_len):
                    layer_weights[j][i] = weights_to_i[j]

            weights.append(layer_weights)

            sum_weights_from_node_to_output.append(np.zeros((prev_layer_len,1)))

        is_bias = - is_bias

    for i, layer_weights in reversed(list(enumerate(weights))):
        for j, w in enumerate(layer_weights):
            if i == len(weights) - 1:
                # on last layer
                for k in range(len(w)):
                    sum_weights_from_node_to_output[i][j] += w[k]
            else:
                for k in range(len(w)):
                    sum_weights_from_node_to_output[i][j] += w[k] * sum_weights_from_node_to_output[i+1][k]

    for i in sum_weights_from_node_to_output[0]:
        print(i[0])

def generate_kingdom():
    new_kingdom = {0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 10}

    # TODO eventually need to randomly select 10 cards for the kingdom
    for i in range(7, params.max_card_id+1):
        if random.random() < 1:
            new_kingdom[i] = 10
        else:
            new_kingdom[i] = 0

    # new_kingdom[9] = 1

    return Kingdom(new_kingdom)

def cards_to_string(cards):
    c_str = []
    for card in cards:
        c_str.append(card.name)
    return c_str

def serialize_cards(cards):
    return [{'name': c.name, 'id': c.id} for c in cards]

def cards_to_ids(cards):
    return [c.id for c in cards]

def get_purchaseable_cards(player, num_coins, kingdom, is_gaining = False):
    cards_purchasable = []

    if params.debug_mode >= 2:
        if is_gaining:
            print(player.name, "gaining with limit", num_coins)
        else:
            print(player.name, "has", num_coins, "coins")

    # "skip" card
    cards_purchasable.append(Card(-1))

    for c in kingdom.supply.keys():
        card = Card(c)
        if card.cost <= num_coins and kingdom.supply[c] > 0:
            cards_purchasable.append(card)

    if params.debug_mode >= 3:
        if is_gaining:
            print(player.name, "gainable:", cards_to_string(cards_purchasable))
        else:
            print(player.name, "purchaseable:", cards_to_string(cards_purchasable))

    return cards_purchasable

def kingdom_to_string(kingdom):
    k_str = ""
    for c,v in kingdom.supply.items():
        card = Card(c)

        k_str += card.name + ": " + str(v) + "   "

    return k_str

# Returns input layer features at given game state buying Card a
def state_features(player, kingdom, a):
    # feature ideas:

    f = []

    f.append(player.coins / 8)
    f.append(a.cost / 8)
    f.append(2 * int(a.f_victory) - 1)
    f.append(2 * int(a.f_treasure) - 1)
    f.append(2 * int(a.f_action) - 1)
    f.append(2 * int(a.f_attack) - 1)
    f.append(2 * int(a.f_curse) - 1)
    f.append(2 * int(a.f_reaction) - 1)
    f.append(kingdom.turn_num * 10 / 30)

    # player vp total
    f.append(player.num_victory_points() / 53)

    # opponent vp total
    f.append(player.opponent.num_victory_points() / 53)

    # opponent - player vp difference
    f.append((player.num_victory_points() - player.opponent.num_victory_points()) / 48)

    # one hot vec of card id
    id_vec = [0 for i in range(params.max_card_id + 2)]
    id_vec[a.id] = 1 # last entry (-1) is always "nothing"
    f.extend(id_vec)

    # num of each card in deck (in total)
    num_in_deck = [0 for i in range(params.max_card_id + 1)]
    for card in player.deck:
        num_in_deck[card.id] += 1
    for card in player.discard:
        num_in_deck[card.id] += 1
    for card in player.in_play:
        num_in_deck[card.id] += 1
    for card in player.hand:
        num_in_deck[card.id] += 1
    # normalize based on initial supply
    for i in range(params.max_card_id + 1):
        if kingdom.supply_initial[i] == 0:
            continue
        num_in_deck[i] = num_in_deck[i] / kingdom.supply_initial[i]
    f.extend(num_in_deck)

    # num of each card remaining in kingdom (normalized by initial supply)
    num_in_kingdom = [j / kingdom.supply_initial[i] if kingdom.supply_initial[i] != 0 else 0 for (i,j) in kingdom.supply.items()]
    f.extend(num_in_kingdom)

    # TODO: should just be a Player function
    # num of each card in opponents deck (in total)
    num_in_opp_deck = [0 for i in range(params.max_card_id + 1)]
    for card in player.opponent.deck:
        num_in_opp_deck[card.id] += 1
    for card in player.opponent.discard:
        num_in_opp_deck[card.id] += 1
    for card in player.opponent.in_play:
        num_in_opp_deck[card.id] += 1
    for card in player.opponent.hand:
        num_in_opp_deck[card.id] += 1
    # normalize based on initial supply
    for i in range(params.max_card_id + 1):
        if kingdom.supply_initial[i] == 0:
            continue
        num_in_opp_deck[i] = num_in_opp_deck[i] / kingdom.supply_initial[i]
    f.extend(num_in_opp_deck)

    # who was starting player
    f.append(kingdom.starting_player)

    # cards in kingdom
    cards_in_kingdom = [int(kingdom.supply_initial[i] > 0) for i in kingdom.supply.keys()]
    f.extend(cards_in_kingdom)

    return Variable(torch.from_numpy(np.array(f)).float())

def force_buy(card_id, player, old_choice):
    print(player.name, "FORCING BUY", Card(card_id).name)
    if player.coins >= Card(card_id).cost and player.kingdom.supply[card_id] > 0:
        return Card(card_id)
    return old_choice

def discard_card(discarded_card, player):
    actual_discard = next(card for card in player.hand if card.id == discarded_card.id)
    assert actual_discard is not None
    player.hand.remove(actual_discard)
    player.discard.append(discarded_card)
    if params.debug_mode >= 3:
        print(player.name, "discarded", discarded_card.name)

def generic_discard_down_to(player, handsize):
    num_to_discard = len(player.hand) - handsize
    for i in range(num_to_discard):
        discarded_card = next((x for x in player.hand if x.f_curse), None)
        if not discarded_card:
            discarded_card = next((x for x in player.hand if (x.f_victory and not x.f_treasure)), None)
        if not discarded_card:
            discarded_card = min(player.hand, key=lambda x: x.cost)

        assert discarded_card is not None

        discard_card(discarded_card, player)

def cards_equivalent(cards1, cards2):
    num_cards_1 = {}
    for c in cards1:
        if c.id not in num_cards_1:
            num_cards_1[c.id] = 0
        num_cards_1[c.id] += 1

    num_cards_2 = {}
    for c in cards2:
        if c.id not in num_cards_2:
            num_cards_2[c.id] = 0
        num_cards_2[c.id] += 1

    return num_cards_1 == num_cards_2

def generic_action_phase(player):
    action_cards = [card for card in player.hand if card.f_action]
    if params.debug_mode >= 3:
        print(player.name, "playable action cards", cards_to_string(action_cards))

    while player.num_actions > 0 and len(action_cards) > 0:
        card_to_play = next((card for card in action_cards if card.gives_actions), None)
        if card_to_play == None:
            card_to_play = max(action_cards, key=lambda card: card.cost)

        assert card_to_play is not None

        player.hand.remove(card_to_play)
        player.in_play.append(card_to_play)
        player.num_actions -= 1
        card_to_play.play(player)
        action_cards = [card for card in player.hand if card.f_action]

# Returns 0 if player lost
# Returns 0.5 if player tied
# Returns 1 if player won
def did_player_win(player_vp, opp_vp, whose_turn, kingdom):
    player_won = player_vp > opp_vp
    if player_vp == opp_vp:
        if whose_turn == kingdom.starting_player:
            # Tie game, both players had equal number of turns
            player_won = 0.5
        else:
            if kingdom.starting_player == 1:
                # Agent had an extra turn, so loses
                player_won = 0
            else:
                # Opponent had extra turn, so agent wins
                player_won = 1

    return player_won