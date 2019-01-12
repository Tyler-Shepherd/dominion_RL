import math
import numpy as np
import random
import torch
from torch.autograd import Variable

from training import params as params
import dominion_utils

# Base functions and training environment for RL

class RL_base():

    def __init__(self, agent):
        self.tau = params.tau_start
        self.learning_rate = params.learning_rate

        self.kingdom_0 = None
        self.kingdom = None
        self.agent = agent
        self.opponent = None
        self.turn_num = None

    '''
    Resets game to beginning
    '''
    def reset_environment(self):
        self.kingdom = self.kingdom_0.copy()

        self.agent.initialize(self.kingdom)
        self.opponent.initialize(self.kingdom)

        self.agent.reset_game()
        self.opponent.reset_game()

        self.trash = []

        self.turn_num = 0

        if params.debug_mode >= 3:
            print("Turn", self.turn_num)

    '''
    Returns -1 if not at goal state (game not over)
    Returns 1 if game is over (no provinces)
    Returns 2 if game is over (3 piles gone)
    '''
    def at_goal_state(self):
        assert self.kingdom[5] >= 0
        if self.kingdom[5] == 0:
            return 1

        num_empty = 0
        for c in self.kingdom.keys():
            if self.kingdom[c] == 0 and self.kingdom_0[c] != 0:
                num_empty += 1

        if num_empty >= 3:
            return 2

        return -1

    '''
    RL reward is the difference in score between player and opponent at end of game
    '''
    def reward(self):
        current_state = self.at_goal_state()

        if current_state == -1:
            # Not a goal state
            reward_val =  0
        else:
            reward_val = self.agent.num_victory_points() - self.opponent.num_victory_points()

        return torch.tensor(reward_val, dtype = torch.float32)

    def get_agent_buy_policy(self):
        legal_actions = self.agent.get_legal_actions()

        if params.debug_mode >= 3:
            print("legal actions:", [c.name for c in legal_actions])

        assert len(legal_actions) > 0 # can always skip buy

        # Boltzmann exploration
        q_vals = []
        self.tau = params.tau_end + (params.tau_start - params.tau_end) * math.exp(
            -1. * self.agent.running_states / params.tau_decay)
        for e in legal_actions:
            q_vals.append(math.exp(self.agent.get_Q_val(e).item() / self.tau))
        q_sum = sum(q_vals)
        probs = []
        for v in q_vals:
            probs.append(v / q_sum)
        legal_actions_index = [i for i in range(len(legal_actions))]
        a = legal_actions[np.random.choice(legal_actions_index, p=probs)]

        assert a is not None

        return a


    def learning_iteration(self):
        # Reset game
        self.reset_environment()

        # 1 if agent turn
        # -1 if opponent turn
        whose_turn = 1 if random.random() < 0.5 else -1
        starting_player = whose_turn

        # While not reached goal state
        while self.at_goal_state() == -1:
            if whose_turn != starting_player:
                self.turn_num += 1

            if whose_turn == 1:
                if params.debug_mode >= 3:
                    self.agent.print_state()

                # Agent's turn
                self.agent.action_phase()

                # TODO extend over multiple buys
                card_to_purchase = self.get_agent_buy_policy()

                # Take the action and update q vals
                self.update_q(card_to_purchase)

                self.agent.clean_up()

                if params.f_learning_rate_decay:
                    # from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html (originally for exploration rate decay)
                    self.learning_rate = params.learning_rate_end + (params.learning_rate_start - params.learning_rate_end) * math.exp(
                        -1. * self.agent.running_states / params.learning_rate_decay)
            else:
                if params.debug_mode >= 3:
                    self.opponent.print_state()

                # Opponent's turn
                self.opponent.action_phase()
                self.opponent.buy_phase()
                self.opponent.clean_up()

            whose_turn = whose_turn * -1


    '''
    Main reinforcement learning loop
    agent is the selected agent for learning
    kingdom is the selected kingdom to play on
    '''
    def reinforcement_loop(self, opponent, kingdom):
        self.opponent = opponent
        self.kingdom_0 = kingdom.copy()
        self.kingdom = kingdom.copy()

        assert params.num_training_iterations % params.update_target_network_every == 0

        for iter in range(params.num_training_iterations):
            self.learning_iteration()

            # update target network
            if iter % params.update_target_network_every == 0:
                self.agent.target_model.load_state_dict(self.agent.model.state_dict())

        return self.agent


    def update_q(self, a):
        old_q_value = self.agent.get_Q_val(a)

        # Agent buys card a
        dominion_utils.buy_card(self.agent, a, self.kingdom)

        if params.debug_mode >= 2:
            print("Agent buying", a.name)

        # Output loss
        self.agent.running_states += 1
        if self.agent.running_states % params.print_loss_every == 0:
            print("*******LOSS:", self.agent.running_loss / params.print_loss_every)
            self.agent.loss_output_file.write(
                str(self.agent.running_states) + '\t' + str(self.agent.running_loss / params.print_loss_every) + '\n')
            self.agent.loss_output_file.flush()

            self.agent.running_loss = 0

        # Gets reward of current (now updated) state
        new_reward = self.reward()

        # Get the maximum estimated q value of all possible actions after buying a
        max_next_q_val = float("-inf")
        next_legal_actions = self.agent.get_legal_actions()
        # TODO ok this doesn't work right now since "next legal actions" at this point is still the same set of cards
        # once implement experience replay need to use the max q val of the next turns buy options

        assert len(next_legal_actions) > 0 # can always skip buy

        for e in next_legal_actions:
            max_next_q_val = max(max_next_q_val, self.agent.get_Q_val(e, use_target_net=True))

        new_q_value = new_reward + params.discount_factor * max_next_q_val

        self.agent.update_q(self.learning_rate, old_q_value, new_q_value)


    def test_agent(self, opponent, kingdom, test_output_full_file):
        self.opponent = opponent
        self.kingdom_0 = kingdom.copy()
        self.kingdom = kingdom.copy()

        # Reset game
        self.reset_environment()

        test_output_full_file.write(str(kingdom) + '\n')

        # 1 if agent turn
        # -1 if opponent turn
        whose_turn = 1 if random.random() < 0.5 else -1
        starting_player = whose_turn

        # While not reached goal state
        while self.at_goal_state() == -1:
            if whose_turn != starting_player:
                self.turn_num += 1

            if whose_turn == 1:
                # Agent's turn
                self.agent.action_phase()
                bought_card = self.agent.buy_phase()

                test_output_full_file.write(str(self.turn_num) + '\t' + str(self.agent.num_coins()) + '\t' + str(bought_card.name) + '\n')

                self.agent.clean_up()
            else:
                # Opponent's turn
                self.opponent.action_phase()
                self.opponent.buy_phase()
                self.opponent.clean_up()

            whose_turn = whose_turn * -1

        player_vp = self.agent.num_victory_points()
        opp_vp = self.opponent.num_victory_points()

        test_output_full_file.write('Player VP\t' + str(player_vp) + '\tOpponent VP\t' + str(opp_vp) + '\tDifference\t' + str(player_vp - opp_vp) + '\n')
        test_output_full_file.write('--------------------------------------------\n')
        test_output_full_file.flush()

        return player_vp > opp_vp, self.turn_num, player_vp, opp_vp
