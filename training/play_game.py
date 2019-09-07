from training import params as params
from training.dominion_agent import Dominion_Agent
from training.RL_base import RL_base
from training.opponents.buy_only_treasure import  Buy_Only_Treasure_Opponent
from kingdom import Kingdom
import dominion_utils

# Run to play a single game
# For manual testing purposes

if __name__ == '__main__':
    agent = Dominion_Agent("")
    base = RL_base(agent)

    model_file = "./training/results/9-3-19/768224832_val_6.pth.tar"
    agent.load_model(model_file)

    dominion_utils.print_feature_weights(agent.model)

    # kingdom = Kingdom({0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0})
    kingdom = dominion_utils.generate_kingdom()
    opponent = Buy_Only_Treasure_Opponent()

    params.debug_mode = 3

    test_output = open('./play_game.txt', 'w+')
    did_it_win, turns_played, player_vp, opp_vp = base.test_agent(opponent, kingdom, test_output)

    print("Win:", did_it_win)
    print("Turns Played:", turns_played)
    print("Player VP", player_vp)
    print("Opp VP", opp_vp)
