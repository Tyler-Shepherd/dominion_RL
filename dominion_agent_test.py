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

if __name__ == '__main__':

    # kingdom = {0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}
    kingdom = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 8, 6: 0}

    agent = dominion_agent()
    agent.load_model("C:\\Users\shepht2\Documents\Computer Science\\Dominion\\dominion_RL\\checkpoint.pth.tar")
    agent.initialize(kingdom)
    agent.reset_environment()

    while agent.at_goal_state() == -1:

        legal_actions = agent.get_legal_actions()

        # Find best action
        max_action = None
        max_action_val = float("-inf")
        for e in legal_actions:
            action_Q_val = agent.get_Q_val(e)
            print(e.name, action_Q_val)
            if action_Q_val > max_action_val:
                max_action = e
                max_action_val = action_Q_val

        print("Max action purchase", max_action.name)
        print("")

        agent.make_move(max_action)