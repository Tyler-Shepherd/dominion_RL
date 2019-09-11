import math
import numpy as np
import random
import torch
import copy
from torch.autograd import Variable

from training import params as params
import dominion_utils

# Base functions and training environment for RL

class Experience_Replay():
    # https://medium.com/ml-everything/reinforcement-learning-with-sparse-rewards-8f15b71d18bf
    def __init__(self, buffer_size=50000, unusual_sample_factor=0.99):
        """ Data structure used to hold game experiences """
        # Buffer will contain [state,action,reward,next_state,done]
        self.buffer = []
        self.buffer_size = buffer_size

        assert unusual_sample_factor <= 1, "unusual_sample_factor has to be <= 1"
        # Setting this value to a low number over-samples experience that had unusually high or low rewards
        self.unusual_sample_factor = unusual_sample_factor

    '''
    param experience is a list of experiences (where each experience is a list of form [state,action,reward,next_state,done]
    '''
    def add(self, experience):
        """ Adds list of experiences to the buffer """
        # Extend the stored experiences
        self.buffer.extend(experience)
        # Keep the last buffer_size number of experiences
        self.buffer = self.buffer[-self.buffer_size:]
        # Keep the extreme values near the top of the buffer for oversampling

    def sample(self, size):
        """ Returns a sample of experiences from the buffer """
        # We want to over-sample frames where things happened. So we'll sort the buffer on the absolute reward
        # (either positive or negative) and apply a geometric probability in order to bias our sampling to the
        # earlier (more extreme) replays
        buffer = sorted(self.buffer, key=lambda replay: abs(replay[2]), reverse=True)
        p = np.array([self.unusual_sample_factor ** i for i in range(len(buffer))])
        p = p / sum(p)
        sample_idxs = np.random.choice(np.arange(len(buffer)), size=size, p=p)
        sample_output = [buffer[idx] for idx in sample_idxs]
        sample_output = np.reshape(sample_output, (size, -1))
        return sample_output

class RL_base():

    def __init__(self, agent):
        self.tau = params.tau_start
        self.learning_rate = params.learning_rate

        self.num_times_trained = 0 # num times experience replay training has occurred
        self.running_states = 0 # num actions taken
        self.running_samples = 0 # num times a sample has been drawn and trained on
        self.running_iters = 0 # num iterations run / games that have been played
        self.buffer = Experience_Replay(buffer_size=params.buffer_size, unusual_sample_factor=params.unusual_sample_factor)

        self.kingdom = None
        self.agent = agent
        self.opponent = None

        # Experience of form [state,action,reward,next_state,done,next_legal_actions]
        self.previous_experience = None
        self.current_experience = None

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
            self.kingdom.print_kingdom()

    '''
    Returns -1 if not at goal state (game not over)
    Returns 1 if game is over (no provinces)
    Returns 2 if game is over (3 piles gone)
    '''
    def at_goal_state(self):
        return self.kingdom.is_game_over()

    '''
    RL reward is the difference in score between player and opponent at end of game
    '''
    def reward(self, bought_card):
        assert "hey" == "this reward makes no sense since tanh has range (-1,1), either update or use RELU"

        current_state = self.at_goal_state()
        if current_state == -1:
            # Not a goal state
            # reward_val =  self.agent.coins / 8
            # reward_val = 0
            # reward_val = (self.agent.num_victory_points() - self.opponent.num_victory_points()) + 48
            reward_val = self.agent.coins + 10 if bought_card.id == 5 else self.agent.coins
        else:
            # reward_val = (self.agent.num_victory_points() - self.opponent.num_victory_points()) + 48
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

        return a, legal_actions

    '''
    Plays a single game, recording experiences
    '''
    def learning_iteration(self):
        # Reset game
        self.reset_environment()

        # 1 if agent turn
        # -1 if opponent turn
        whose_turn = self.kingdom.starting_player

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
                    card_to_purchase, purchasable_cards = self.get_agent_buy_policy()

                    # Take the action and update q vals
                    self.agent_purchase(card_to_purchase, purchasable_cards)

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

    '''
    Main reinforcement learning loop
    Plays on kingdom against opponent
    '''
    def reinforcement_loop(self, opponent, kingdom):
        self.opponent = opponent
        self.kingdom = copy.deepcopy(kingdom)

        self.agent.opponent = self.opponent
        self.opponent.opponent = self.agent

        assert params.num_train_kingdoms * params.num_training_iterations % params.train_from_experiences_every_iterations == 0
        assert (params.num_train_kingdoms * params.num_training_iterations / params.train_from_experiences_every_iterations) % params.update_target_network_every == 0

        for iter in range(params.num_training_iterations):
            self.learning_iteration()
            self.running_iters += 1

            # Train on samples from experience replay buffer
            if self.running_iters % params.train_from_experiences_every_iterations == 0:
                print("Starting training after {} iterations".format(self.running_iters))
                self.train()

    '''
    Has agent purchase card a, saves experience in replay buffer
    '''
    def agent_purchase(self, a, legal_actions):
        # Experience of form [state,action,reward,next_state,done,next_legal_actions]
        if self.previous_experience is not None:
            # Add legal actions to the experience from two steps ago
            self.previous_experience.append(legal_actions)
            # Experience completed - add to buffer
            self.buffer.add([self.previous_experience.copy()])
        if self.current_experience is not None:
            # Add next_state to the previous experience before starting new experience
            self.current_experience.append(self.agent.get_state())
            self.current_experience.append(self.at_goal_state() != -1)
            self.previous_experience = self.current_experience.copy()

        self.current_experience = []
        self.current_experience.append(self.agent.get_state())
        self.current_experience.append(a)

        # Agent buys card a
        dominion_utils.buy_card(self.agent, a, self.kingdom)
        self.running_states += 1

        new_reward = self.reward(a)
        self.current_experience.append(new_reward)

    '''
    Samples from experience replay buffer to train agent
    '''
    def train(self):
        if len(self.buffer.buffer) == 0:
            # Nothing in buffer, nothing to train
            return

        samples = self.buffer.sample(params.batch_size)

        for s in samples:
            #[state, action, reward, next_state, done, next_legal_actions]
            assert len(s) == 6
            state = s[0]
            action = s[1]
            reward = s[2]
            next_state = s[3]
            done = s[4]
            next_legal_actions = s[5]

            self.agent.set_state(state)
            old_q_value = self.agent.get_Q_val(action)
            self.agent.set_state(next_state)

            if done:
                max_next_q_val = 0
            else:
                # Get the maximum estimated q value of all possible actions after buying a
                max_next_q_val = float("-inf")

                assert len(next_legal_actions) > 0 # can always skip buy

                for e in next_legal_actions:
                    max_next_q_val = max(max_next_q_val, self.agent.get_Q_val(e, use_target_net=True))

            new_q_value = reward + params.discount_factor * max_next_q_val
            self.agent.update_q(self.learning_rate, old_q_value, new_q_value)

            self.running_samples += 1
            if params.f_learning_rate_decay:
                # from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html (originally for exploration rate decay)
                self.learning_rate = params.learning_rate_end + (params.learning_rate_start - params.learning_rate_end) * math.exp(
                    -1. * self.running_samples / params.learning_rate_decay)

        # avg loss per sample
        loss_avg = self.agent.running_loss / params.batch_size
        print("Experience Replay Training {:d}, LOSS {:f}".format(self.num_times_trained, loss_avg))
        self.agent.loss_output_file.write(str(self.num_times_trained) + '\t' + str(loss_avg) + '\n')
        self.agent.loss_output_file.flush()

        self.agent.running_loss = 0
        self.num_times_trained += 1

        # update target network
        if self.num_times_trained % params.update_target_network_every == 0:
            self.agent.target_model.load_state_dict(self.agent.model.state_dict())

        # Don't need to reset agent state since training only occurs at end of a game

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

        test_output_full_file.write(str(kingdom.supply) + " " + opponent.name + '\n')

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

        test_output_full_file.write('Player VP\t' + str(player_vp) + '\tOpponent VP\t' + str(opp_vp) + '\tDifference\t' + str(player_vp - opp_vp) + '\tWinner\t' + str(player_won) + '\n')
        test_output_full_file.write('--------------------------------------------\n')
        test_output_full_file.flush()

        assert 1 == 2 # should use dominion_utils.did_player_win

        return player_won, self.kingdom.turn_num, player_vp, opp_vp
