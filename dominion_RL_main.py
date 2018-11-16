import io
import os
import math
import time
import numpy as np
from numpy import *
from numpy import linalg as LA
import itertools
import copy
import sys
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from queue import PriorityQueue
import torch
from torch.autograd import Variable
import random
from pprint import pprint
import glob
import datetime

from RL_base import RL_base
from dominion_agent import dominion_agent
import params as params


def test_model(test_output_file, agent, test_kingdoms, num_times_tested, val_testing):
    # Test the agents learned model

    num_won = 0
    num_total_turns = 0
    num_total_player_vp = 0
    num_total_opp_vp = 0
    j = 0

    # TODO is_val, num_times_tested
    if val_testing:
        print("---------------Validation " + str(num_times_tested) + "--------------")
    else:
        print("---------------Test " + str(num_times_tested) + "----------------")

    for test_kingdom in test_kingdoms:
        player_won, test_num_turns, player_vp, opp_vp = agent.test_model(test_kingdom)

        num_won += player_won
        num_total_turns += test_num_turns
        num_total_player_vp += player_vp
        num_total_opp_vp += opp_vp

        j += 1

    win_percent = num_won / len(test_kingdoms)
    avg_num_turns = num_total_turns / len(test_kingdoms)
    avg_player_vp = num_total_player_vp / len(test_kingdoms)
    avg_opp_vp = num_total_opp_vp / len(test_kingdoms)

    print("Agent won", win_percent, ", took average of", avg_num_turns, "turns with avg VP score of", avg_player_vp, "and opp VP score of", avg_opp_vp)
    test_output_file.write(str(num_times_tested) + "\t" + str(num_won) + '\t' + str(win_percent) + '\t'
                           + str(num_total_turns) + "\t" + str(avg_num_turns) + "\t"
                           + str(num_total_player_vp) + "\t" + str(avg_player_vp) + "\t"
                           + str(num_total_opp_vp) + "\t" + str(avg_opp_vp) + "\n")
    test_output_file.flush()

    return win_percent


if __name__ == '__main__':
    # Set random seeds
    random.seed(time.time())
    torch.manual_seed(time.time())

    # Make the kingdoms
    train_kingdoms = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 1
    test_kingdoms = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 1
    val_kingdoms = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 1

    # Identifying id for this run
    model_id = random.randint(0, 1000000000)
    print("model_id", model_id)

    # Open files for output
    output_filename = "results/" + str(model_id) + '_training.txt'
    loss_filename = "results/" + str(model_id) + "_loss.txt"
    test_output_filename = "results/" + str(model_id) + "_test.txt"
    val_output_filename = "results/" + str(model_id) + "_val.txt"
    output_file = open(output_filename, "w+")
    loss_file = open(loss_filename, "w+")
    test_output_file = open(test_output_filename, "w+")
    val_file = open(val_output_filename, "w+")

    loss_file.write('Num States' + '\t' + 'Loss Per State' + '\n')
    loss_file.flush()

    # Make agent and base
    agent = dominion_agent(loss_file)
    base = RL_base()

    # Counter variables
    i = 0
    total_time = 0
    total_num_turns = 0

    # Print header
    header = "Kingdom\tTurns\tPlayer Won\tOpponent VP\tPlayer VP\tRuntime"
    print(header)
    output_file.write(header+'\n')

    parameters_output_filename = "results/" + str(model_id) + "_parameters.txt"
    parameters_file = open(parameters_output_filename, "w+")
    params.print_params(parameters_file)

    # print training and test kingdoms used
    parameters_file.write("\nTraining Kingdoms\n")
    for kingdom in train_kingdoms:
        parameters_file.write(str(kingdom) + "\n")
    parameters_file.write("\nTest Kingdoms\n")
    for kingdom in test_kingdoms:
        parameters_file.write(str(kingdom) + "\n")
    parameters_file.flush()

    test_header = "Num Test\tNum Won\tWin Percent\tNum Total Turns\tAvg Num Turns\tTotal Agent VP\tAvg Agent VP\tTotal Opponent VP\tAvg Opponent VP\n"
    test_output_file.write(test_header)
    val_file.write(test_header)
    test_output_file.flush()
    val_file.flush()

    val_results = []
    num_times_tested = 0

    for epoch in range(params.num_epochs):
        i = 0
        print('---------------Epoch ' + str(epoch) + '------------------------')

        # Shuffle training data
        random.shuffle(train_kingdoms)

        for kingdom in train_kingdoms:
            # Run the agent
            start = time.perf_counter()
            base.reinforcement_loop(agent, kingdom)
            end = time.perf_counter()

            total_time += (end - start)

            # if want > 1 training iteration, need to save num times won, vp over multiple iterations in base
            assert params.num_training_iterations == 1

            player_vp = agent.player.num_victory_points()
            opp_vp = agent.opponent.player.num_victory_points()

            result_text = "%s\t%d\t%d\t%d\t%d\t%f" % (str(kingdom), agent.turn_num, player_vp > opp_vp, opp_vp, player_vp, end - start)
            print(i, result_text)
            output_file.write(result_text + '\n')
            output_file.flush()

            i += 1

        # test on validation data after each epoch
        num_won = test_model(val_file, agent, val_kingdoms, num_times_tested, True)
        val_results.append(num_won)
        num_times_tested += 1

    print('----------------------Training Done------------------------------')
    print("Validation results:", val_results)
    best_model = np.argmin(val_results)
    print("Best model:", best_model)

    # TODO load best model

    # Final test
    for t in range(10):
        test_model(test_output_file, agent, test_kingdoms, "final_" + str(t), False)

    # Close files
    output_file.close()
    loss_file.close()
    test_output_file.close()
    val_file.close()
    parameters_file.close()

    print("Total Time to Train: %f" % total_time)
    print("Average Time: %f" % (total_time / len(train_kingdoms)))