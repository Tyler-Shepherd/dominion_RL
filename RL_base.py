import io
import os
import math
import time
import numpy as np
from numpy import *
import itertools
from profile import Profile
import copy
import sys
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from queue import PriorityQueue
import random
from pprint import pprint
import glob

import params as params

# Base functions and training environment for RL

class RL_base():

    def __init__(self):
        self.tau = params.tau_start
        pass


    def learning_iteration(self, agent):
        # Reset environment
        agent.reset_environment()

        # While not reached goal state
        while agent.at_goal_state() == -1:
            legal_actions = agent.get_legal_actions()

            if params.debug_mode >= 3:
                agent.print_state()
                print("legal actions:", [c.name for c in legal_actions])

            if len(legal_actions) == 0:
                # No possible actions
                if params.debug_mode >= 2:
                    print("no purchaseable cards")
                # TODO what should happen in this case?
                break

            # Boltzmann exploration
            q_vals = []
            self.tau = params.tau_end + (params.tau_start - params.tau_end) * math.exp(
                -1. * agent.running_states / params.tau_decay)
            for e in legal_actions:
                q_vals.append(exp(agent.get_Q_val(e).item() / self.tau))
            q_sum = sum(q_vals)
            probs = []
            for v in q_vals:
                probs.append(v / q_sum)
            legal_actions_index = [i for i in range(len(legal_actions))]
            a = legal_actions[np.random.choice(legal_actions_index, p=probs)]

            # epsilon greedy
            # if random.random() < params.exploration_rate:
            #     # Randomly select a possible action with probability epsilon
            #     i = random.randint(0, len(legal_actions) - 1)
            #     a = legal_actions[i]
            #     if params.debug_mode >= 3:
            #         print("randomly select action", a.name)
            # else:
            #     # Otherwise greedily choose best action
            #     max_action = None
            #     max_action_val = float("-inf")
            #     for e in legal_actions:
            #         action_Q_val = agent.get_Q_val(e)
            #         if action_Q_val > max_action_val:
            #             max_action = e
            #             max_action_val = action_Q_val
            #
            #     a = max_action
            #     if params.debug_mode >= 3:
            #         print("greedily select action", a.name, "with q val", max_action_val.item())

            assert a is not None

            # Take the action and update q vals
            self.update_q(agent, a)

            if params.f_learning_rate_decay:
                # from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html (originally for exploration rate decay)
                self.learning_rate = params.learning_rate_end + (params.learning_rate_start - params.learning_rate_end) * math.exp(
                    -1. * agent.running_states / params.learning_rate_decay)


    '''
    Main reinforcement learning loop
    agent is the selected agent for learning
    env0 is the data given for initializing the environment (i.e. a profile)
    '''
    def reinforcement_loop(self, agent, env0):
        # Initialize
        agent.initialize(env0)

        assert params.num_training_iterations % params.update_target_network_every == 0

        for iter in range(params.num_training_iterations):
            self.learning_iteration(agent)

            # update target network
            if iter % params.update_target_network_every == 0:
                agent.target_model.load_state_dict(agent.model.state_dict())

        return agent


    def update_q(self, agent, a):
        old_q_value = agent.get_Q_val(a)

        # Actually updates the agent state
        agent.make_move(a)

        # Gets reward of current (now updated) state
        new_reward = agent.reward()

        # Get the maximum estimated q value of all possible actions after buying a
        max_next_q_val = float("-inf")
        next_legal_actions = agent.get_legal_actions()

        if len(next_legal_actions) == 0:
            # If there are no legal next actions, then we've reached a goal state
            # Estimate of next state is just 0 (since there is no next state)
            # TODO what does this mean
            max_next_q_val = 0

        for e in next_legal_actions:
            max_next_q_val = max(max_next_q_val, agent.get_Q_val(e, use_target_net=True))

        new_q_value = new_reward + params.discount_factor * max_next_q_val

        agent.update_q(params.learning_rate, old_q_value, new_q_value)