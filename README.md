# dominion_RL
Building an AI for the card game "Dominion" through online reinforcement learning (q-learning) with neural networks.

In /training, two different training algorithms are available. dominion_RL_main.py is the main file to run. Using RL_base.py does a classic q-learning algorithms with neural networks for each state policy. Using RL_DAgger uses the DAgger algorithm (Dataset Aggregation) to learn. params.py contains configurable parameters.

In /app, an Angular Flask app is available to play against your trained agent.

For those curious, the following papers address different methods of AIs for Dominion:

  "An AI for Dominion Based on Monte-Carlo Methods" - Jon Vegard Jansen and Robin Tollisen. https://pdfs.semanticscholar.org/28b6/ada13e948cfaee4af5138ee667d404eb01ac.pdf
  
  "Developing an agent for Dominion using modern AI-approaches" - Rasmus Bille Fynbo and Miguel A. Sicart for University of Copenhagen. (Paper doesn't seem available anymore)

  "Evolving Card Sets Towards Balancing Dominion" - Tobias Mahlmann, Julian Togelius and Georgios N. Yannakakis. http://julian.togelius.com/Mahlmann2012Evolving.pdf
  
