import math
import numpy as np
import random
import torch
import copy
from torch.autograd import Variable

from card import Card
from training import params as params
import dominion_utils

# Base functions and training environment for RL

class RL_DAgger():

    def __init__(self, agent):
        self.tau = params.tau_start
        self.learning_rate = params.learning_rate

        self.num_times_trained = 0 # num times experience replay training has occurred
        self.running_states = 0 # num actions taken
        self.running_samples = 0 # num times a sample has been drawn and trained on
        self.running_iters = 0 # num iterations run / games that have been played

        self.kingdom = None
        self.agent = agent
        self.opponent = None

    '''
    Resets game to beginning
    '''
    def reset_environment(self):
        self.kingdom.reset()

        self.agent.initialize(self.kingdom)
        self.opponent.initialize(self.kingdom)

        self.agent.reset_game()
        self.opponent.reset_game()

        self.previous_experience = None
        self.current_experience = None

        if params.debug_mode >= 2:
            print("New Game")

    '''
    Returns -1 if not at goal state (game not over)
    Returns 1 if game is over (no provinces)
    Returns 2 if game is over (3 piles gone)
    '''
    def at_goal_state(self):
        return self.kingdom.is_game_over()

    '''
    RL reward is the VP score at end of game, with bonus for winning
    '''
    def reward(self):
        current_state = self.at_goal_state()

        assert current_state > 0
        reward_val = 100 if self.agent.num_victory_points() > self.opponent.num_victory_points() else self.agent.num_victory_points()

        if params.debug_mode >= 3:
            print("Reward", reward_val)
        return torch.tensor(reward_val, dtype = torch.float32)

    def get_agent_buy_policy(self):
        legal_actions = self.agent.get_legal_actions()

        if params.debug_mode >= 3:
            print("legal actions:", [c.name for c in legal_actions])

        assert len(legal_actions) > 0 # can always skip buy

        # Boltzmann exploration
        q_vals = []
        self.tau = params.tau_end + (params.tau_start - params.tau_end) * math.exp(
            -1. * self.running_states / params.tau_decay)
        for e in legal_actions:
            q_vals.append(math.exp(self.agent.get_Q_val(e).item() / self.tau))
        q_sum = sum(q_vals)
        probs = []
        for v in q_vals:
            probs.append(v / q_sum)
        legal_actions_index = [i for i in range(len(legal_actions))]

        if not np.isclose(sum(probs), [1]):
            print(sum(probs))
            print(probs)
            print(q_vals)
            print(q_sum)

        a = legal_actions[np.random.choice(legal_actions_index, p=probs)]

        assert a is not None

        return a

    '''
    Plays a single game, recording strategy
    '''
    def sample_strategy(self):
        # Reset game
        self.reset_environment()

        # 1 if agent turn
        # -1 if opponent turn
        whose_turn = self.kingdom.starting_player

        strategy = []

        # While not reached goal state
        while self.at_goal_state() == -1:
            if whose_turn != self.kingdom.starting_player:
                self.kingdom.next_turn()

            if whose_turn == 1:
                if params.debug_mode >= 3:
                    self.agent.print_state()
                    self.kingdom.print_kingdom()

                # Agent's turn
                self.agent.action_phase()

                while self.agent.num_buys > 0:
                    card_to_purchase = self.get_agent_buy_policy()

                    # Take the action
                    self.agent_purchase(card_to_purchase)

                    strategy.append((self.agent.get_state(), card_to_purchase.id))

                self.agent.clean_up()

            else:
                if params.debug_mode >= 3:
                    self.opponent.print_state()
                    self.kingdom.print_kingdom()

                # Opponent's turn
                self.opponent.action_phase()
                self.opponent.buy_phase()
                self.opponent.clean_up()

            whose_turn = whose_turn * -1

        return strategy, self.reward()

    '''
    Main reinforcement learning loop
    Plays on kingdom against opponent
    '''
    def reinforcement_loop(self, opponent, kingdom):
        self.opponent = opponent
        self.kingdom = copy.deepcopy(kingdom)

        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

        Q = {}  # strategy -> game reward

        for iter in range(params.num_dagger_iterations):
            print("---------------Iteration " + str(iter) + '-----------------', flush=True)

            # Sample strategies: play games
            print("------Sampling Strategies-----------", flush=True)
            with torch.no_grad():
                for k in range(params.num_dagger_samples):
                    strategy, game_reward = self.sample_strategy()
                    Q[strategy] = max(Q[strategy], game_reward) if strategy in Q else game_reward

            print("------Extracting Training Data-----------", flush=True)
            R = {} # R is dictionary of game_state -> dict of bought_card -> best reward achieved by buying that card
            for (strategy, game_reward) in Q.items():
                # strategy is list (Player State, bought_card id)
                for (s, c) in strategy:
                    # (s,c) = (Player State, card id)
                    if s not in R:
                        R[s] = {}
                    if c not in R[s]:
                        R[s][c] = game_reward
                    else:
                        R[s][c] = max(game_reward, R[s][c])


            print("------Training Policy-----------", flush=True)
            # for each item in R, do q learning
            for (s, C) in R.items():
                # s is state
                # C is dict of card -> best reward
                self.agent.set_state(s)

                for (card_id, game_reward) in C.items():
                    old_q_value = self.agent.get_Q_val(Card(card_id))

                    self.agent.update_q(self.learning_rate, old_q_value, game_reward)

    '''
    Has agent purchase card a, saves experience in replay buffer
    '''
    def agent_purchase(self, a):
        # Agent buys card a
        dominion_utils.buy_card(self.agent, a, self.kingdom)
        self.running_states += 1

        if params.debug_mode >= 2:
            print("Agent buying", a.name)

    '''
    Plays one game using current agent against opponent on kingdom, and prints output to test_output_full_file
    '''
    def test_agent(self, opponent, kingdom, test_output_full_file):
        self.opponent = opponent
        self.kingdom = copy.deepcopy(kingdom)

        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

        # Reset game
        self.reset_environment()

        test_output_full_file.write(str(kingdom.supply) + '\n')

        # 1 if agent turn
        # -1 if opponent turn
        whose_turn = self.kingdom.starting_player

        # While not reached goal state
        while self.at_goal_state() == -1:
            if whose_turn == self.kingdom.starting_player:
                self.kingdom.next_turn()

            if whose_turn == 1:
                # Agent's turn
                self.agent.action_phase()
                purchases = self.agent.buy_phase()

                for coins, bought_card in purchases:
                    test_output_full_file.write(str(self.kingdom.turn_num) + '\t' + str(coins) + '\t' + str(bought_card.name) + '\n')

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

        player_won = player_vp > opp_vp
        if player_vp == opp_vp:
            if whose_turn == self.kingdom.starting_player:
                # Tie game, both players had equal number of turns
                player_won = 0
            else:
                if self.kingdom.starting_player == 1:
                    # Agent had an extra turn, so loses
                    player_won = 0
                else:
                    # Opponent had extra turn, so agent wins
                    player_won = 1

        return player_won, self.kingdom.turn_num, player_vp, opp_vp