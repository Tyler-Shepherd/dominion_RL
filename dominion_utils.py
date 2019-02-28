import numpy as np
import random
import torch
from torch.autograd import Variable

import training.params as params
from card import Card
from kingdom import Kingdom

def buy_card(player, card, kingdom):
    if card.id != -1:
        kingdom.buy_card(card)
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
    max_card_id = 6
    new_kingdom = {0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8}

    # TODO eventually need to randomly select 10 cards for the kingdom
    for i in range(6, max_card_id+1):
        if random.random() < 0.5:
            new_kingdom[i] = 10
        else:
            new_kingdom[i] = 0

    return Kingdom(new_kingdom)

def cards_to_string(cards):
    c_str = []
    for card in cards:
        c_str.append(card.name)
    return c_str

def get_purchaseable_cards(num_coins, kingdom):
    cards_purchasable = []

    for c in kingdom.supply.keys():
        card = Card(c)
        if card.cost <= num_coins and kingdom.supply[c] > 0:
            cards_purchasable.append(card)

    return cards_purchasable

def kingdom_to_string(kingdom):
    k_str = ""
    for c,v in kingdom.supply.items():
        card = Card(c)

        k_str += card.name + ": " + str(v) + "   "

    return k_str

# Returns input layer features at given game state buying Card a
def state_features(player, kingdom, a):
    # num remaining of each card in kingdom, num of each card in deck
    # num of each card opponent has, opponent vp total
    # one-hot vector for a's id
    # special for if a is Nothing?
    # who was starting player

    f = []
    f.append(player.coins)
    f.append(a.cost)
    f.append(player.coins - a.cost)
    f.append(2 * int(a.f_victory) - 1)
    f.append(2 * int(a.f_treasure) - 1)
    f.append(2 * int(a.f_action) - 1)
    f.append(kingdom.turn_num)

    # player vp total
    f.append(player.num_victory_points())

    # opponent vp total
    f.append(player.opponent.num_victory_points())

    # opponent - player vp difference
    f.append(player.num_victory_points() - player.opponent.num_victory_points())

    return Variable(torch.from_numpy(np.array(f)).float())
