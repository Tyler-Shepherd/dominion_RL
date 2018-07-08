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


def test_model(test_output_file, agent, test_kingdoms):
    # Test the agents learned model

    num_total_turns = 0
    num_total_vp = 0
    j = 0

    print("starting test")

    for test_kingdom in test_kingdoms:
        test_num_turns, test_vp = agent.test_model(test_kingdom)

        num_total_turns += test_num_turns
        num_total_vp += test_vp

        j += 1

    avg_num_turns = num_total_turns / len(test_kingdoms)
    avg_vp = num_total_vp / len(test_kingdoms)

    print("Test took average of", avg_num_turns, "turns with avg VP score of", avg_vp)
    test_output_file.write(str(i) + "\t" + str(num_total_turns) + "\t" + str(avg_num_turns) + "\t" + str(num_total_vp) + "\t" + str(avg_vp) + "\n")
    test_output_file.flush()


# After how many kingdoms to test the model
test_every = 2500

# Whether or not to test before any training
test_at_start = 0


if __name__ == '__main__':
    agent = dominion_agent()
    base = RL_base()

    # Set random seeds
    random.seed(time.time())
    torch.manual_seed(time.time())

    test_kingdoms = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 20000
    train_kingdoms = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 80000

    # Open files for output
    output_filename = "results/results_" + os.path.basename(__file__)
    output_filename = output_filename.replace('.py','')
    weight_filename = output_filename + "_weights.txt"
    loss_filename = output_filename + "_loss.txt"
    test_output_filename = output_filename + "_test_output.txt"
    parameters_output_filename = output_filename + "_parameters.txt"
    output_filename += '.txt'
    output_file = open(output_filename, "w+")
    weight_file = open(weight_filename, "w+")
    loss_file = open(loss_filename, "w+")
    test_output_file = open(test_output_filename, "w+")
    parameters_file = open(parameters_output_filename, "w+")

    total_time = 0

    total_num_turns = 0

    # Counter variable
    i = 0

    # Print header
    header = "Kingdom\tTurns\tPlayer Won\tOpponent VP\tPlayer VP\tRuntime"
    print(header)
    output_file.write(header+'\n')

    # Print parameters
    parameters_file.write("Num Training Data\t" + str(len(train_kingdoms)) + '\n')
    parameters_file.write("Num Testing Data\t" + str(len(test_kingdoms)) + '\n')
    parameters_file.write("Learning Rate\t" + str(base.learning_rate) + '\n')
    parameters_file.write("Discount Factor\t" + str(base.discount_factor) + '\n')
    parameters_file.write("Exploration Rate\t" + str(base.exploration_rate) + '\n')
    parameters_file.write("Num Iterations per Profile\t" + str(base.num_iterations) + '\n')
    parameters_file.write("Agent D_in\t" + str(agent.D_in) + '\n')
    parameters_file.write("Agent H\t" + str(agent.H) + '\n')
    parameters_file.write("Agent D_out\t" + str(agent.D_out) + '\n')
    parameters_file.write("Agent Model\t" + str(agent.model) + '\n')
    parameters_file.write("Agent Loss Function\t" + str(agent.loss_fn) + '\n')
    parameters_file.write("Date\t" + str(datetime.datetime.now()) + '\n')

    # print training and test kingdoms used
    parameters_file.write("\nTraining Kingdoms\n")
    for kingdom in train_kingdoms:
        parameters_file.write(str(kingdom) + "\n")

    parameters_file.write("\nTest Kingdoms\n")
    for kingdom in test_kingdoms:
        parameters_file.write(str(kingdom) + "\n")

    parameters_file.flush()

    test_output_file.write("Num Trained\tTotal Num Turns\tAvg Num Turns\tTotal VP\tAvg VP\n")

    for kingdom in train_kingdoms:
        if i % test_every == 0 and (test_at_start or i != 0):
           test_model(test_output_file, agent, test_kingdoms)

        # Run the agent
        start = time.perf_counter()
        base.reinforcement_loop(agent, kingdom)
        end = time.perf_counter()

        total_time += (end - start)

        player_vp = agent.player.num_victory_points()
        opp_vp = agent.opponent.player.num_victory_points()

        result_text = "%s\t%d\t%d\t%d\t%d\t%f" % (str(kingdom), agent.turn_num, player_vp > opp_vp, opp_vp, player_vp, end - start)
        print(i, result_text)
        output_file.write(result_text + '\n')
        output_file.flush()

        # agent.print_model(weight_file)

        #for loss in stats.loss:
            #loss_file.write(str(loss) + '\n')
        #loss_file.write('\n')
        #loss_file.flush()

        i += 1

    # Final test
    test_model(test_output_file, agent, test_kingdoms)

    # Close files
    output_file.close()
    weight_file.close()
    loss_file.close()
    test_output_file.close()
    parameters_file.close()

    print("Total Time to Train: %f" % total_time)
    print("Average Time: %f" % (total_time / len(train_kingdoms)))