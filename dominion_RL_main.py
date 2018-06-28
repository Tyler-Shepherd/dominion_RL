import io
import os
import math
import time
import numpy as np
from numpy import *
from numpy import linalg as LA
import itertools
from profile import Profile
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

from RL_base import RL_base
from dominion_agent import dominion_agent


def test_model(test_output_file, agent, test_kingdoms):
    # Test the agents learned model

    num_total_turns = 0
    num_total_vp = 0
    j = 0

    for test_kingdom in test_kingdoms:
        print("Testing", test_kingdom)

        test_num_turns, test_vp = agent.test_model(test_kingdom)

        num_total_turns += test_num_turns
        num_total_vp += test_vp

        j += 1

    print("Test took average of", num_total_turns / len(test_kingdoms), "turns with avg VP score of", num_total_vp / len(test_kingdoms))
    test_output_file.write(str(i) + "\t" + str(num_total_turns) + "\n")
    test_output_file.flush()


# After how many profiles to test the model
test_every = 25

# Whether or not to test before any training
test_at_start = 1

# Number of iterations to use when testing
num_test_iterations = 10


if __name__ == '__main__':
    agent = dominion_agent()
    base = RL_base()

    # Set random seeds
    random.seed(time.time())
    torch.manual_seed(time.time())

    test_filenames = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 20
    filenames = [{0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}] * 100

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

    num_profiles = 0
    total_time = 0

    total_num_turns = 0

    # Counter variable
    i = 0

    # Print header
    header = "Inputfile\tTurns\tRuntime"
    print(header)
    output_file.write(header+'\n')

    # Print parameters
    # TODO
    # parameters_file.write("Data Path\t" + rpconfig.path + '\n')
    # parameters_file.write("Train\t" + str(len(filenames)) + '\n')
    # parameters_file.write("Test\t" + str(len(test_filenames)) + '\n')
    # parameters_file.write("Num Iterations per Profile\t" + MechanismRankedPairs().num_iterations + '\n')

    for kingdom in filenames:
        if i % test_every == 0 and (test_at_start or i != 0):
           test_model(test_output_file, agent, test_filenames)

        # Run the agent
        start = time.perf_counter()
        base.reinforcement_loop(agent, kingdom)
        end = time.perf_counter()

        total_time += (end - start)
        num_profiles += 1

        result_text = "%s\t%f" % (str(kingdom), end - start)
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
    test_model(test_output_file, agent, test_filenames)

    # Close files
    output_file.close()
    weight_file.close()
    loss_file.close()
    test_output_file.close()
    parameters_file.close()

    print("Total Time to Train: %f" % total_time)
    print("Average Time: %f" % (total_time / num_profiles))