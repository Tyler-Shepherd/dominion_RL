# dominion_RL
Building an AI for the card game "Dominion" through online reinforcement learning (q-learning) with neural networks.

In /training, two different training algorithms are available. dominion_RL_main.py is the main file to run. Using RL_base.py does a classic q-learning algorithms with neural networks for each state policy. Using RL_DAgger uses the DAgger algorithm (Dataset Aggregation) to learn. params.py contains configurable parameters.

In /app, an Angular app is available to play against your trained agent.
