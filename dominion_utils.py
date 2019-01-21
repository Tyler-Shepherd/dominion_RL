import training.params as params
import numpy as np
import random
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
