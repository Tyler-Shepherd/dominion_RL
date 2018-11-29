from RL_base import RL_base
from dominion_agent import dominion_agent
import params as params

if __name__ == '__main__':
    agent = dominion_agent("")

    model_file = "C:\\Users\\shepht2\\Documents\\Computer Science\\Dominion\\dominion_RL\\results\\"
    model_file += "717317245_val_1.pth.tar"
    agent.load_model(model_file)

    kingdom = {0: 30, 1: 30, 2: 30, 3: 8, 4: 8, 5: 8, 6: 0}

    params.debug_mode = 3

    did_it_win, turns_played, player_vp, opp_vp = agent.test_model(kingdom)

    print("Win:", did_it_win)
    print("Turns Played:", turns_played)
    print("Player VP", player_vp)
    print("Opp VP", opp_vp)
