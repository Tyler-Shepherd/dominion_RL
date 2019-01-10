import math
import numpy as np
from training import params as params

# Base functions and training environment for RL

class RL_base():

    def __init__(self):
        self.tau = params.tau_start
        self.learning_rate = params.learning_rate

        self.kingdom_0 = None
        self.kingdom = None
        self.agent = None
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

        self.turn_num = 1

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

    def learning_iteration(self):
        # Reset game
        self.reset_environment()

        # While not reached goal state
        while self.at_goal_state() == -1:
            legal_actions = self.agent.get_legal_actions()

            if params.debug_mode >= 3:
                self.agent.print_state()
                print("legal actions:", [c.name for c in legal_actions])

            if len(legal_actions) == 0:
                # No possible actions
                if params.debug_mode >= 2:
                    print("no purchaseable cards")
                # TODO what should happen in this case?
                # shouldn't ever be possible due to 'skip buy' action right?
                break

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

            # Take the action and update q vals
            self.update_q(a)

            if params.f_learning_rate_decay:
                # from https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html (originally for exploration rate decay)
                self.learning_rate = params.learning_rate_end + (params.learning_rate_start - params.learning_rate_end) * math.exp(
                    -1. * self.agent.running_states / params.learning_rate_decay)


    '''
    Main reinforcement learning loop
    agent is the selected agent for learning
    kingdom is the selected kingdom to play on
    '''
    def reinforcement_loop(self, agent, opponent, kingdom):
        self.agent = agent
        self.opponent = opponent
        self.kingdom_0 = kingdom.copy()
        self.kingdom = kingdom.copy()

        assert params.num_training_iterations % params.update_target_network_every == 0

        for iter in range(params.num_training_iterations):
            self.learning_iteration()

            # update target network
            if iter % params.update_target_network_every == 0:
                agent.target_model.load_state_dict(agent.model.state_dict())

        return agent


    def update_q(self, a):
        old_q_value = self.agent.get_Q_val(a)

        # Actually updates the agent state
        self.agent.make_move(a)

        # Gets reward of current (now updated) state
        new_reward = self.agent.reward()

        # Get the maximum estimated q value of all possible actions after buying a
        max_next_q_val = float("-inf")
        next_legal_actions = self.agent.get_legal_actions()

        if len(next_legal_actions) == 0:
            # If there are no legal next actions, then we've reached a goal state
            # Estimate of next state is just 0 (since there is no next state)
            # TODO what does this mean
            max_next_q_val = 0

        for e in next_legal_actions:
            max_next_q_val = max(max_next_q_val, self.agent.get_Q_val(e, use_target_net=True))

        new_q_value = new_reward + params.discount_factor * max_next_q_val

        self.agent.update_q(self.learning_rate, old_q_value, new_q_value)