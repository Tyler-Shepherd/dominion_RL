import random
import time

import torch
import numpy as np

import training.params as params
from training.RL_base import RL_base
from training.RL_DAgger import  RL_DAgger
from training.dominion_agent import Dominion_Agent
from training.opponents.buy_only_treasure import Buy_Only_Treasure_Opponent
from training.opponents.dummy import Dummy_Opponent
from kingdom import Kingdom
import dominion_utils

def test_model(test_output_file, test_output_full_file, base, test_kingdoms, num_times_tested, val_testing):
    # Test the agents learned model

    num_won = 0
    num_total_turns = 0
    num_total_player_vp = 0
    num_total_opp_vp = 0

    test_output_full_file.write("************** Test " + str(num_times_tested) + '\n')

    if val_testing:
        print("---------------Validation " + str(num_times_tested) + "--------------")
    else:
        print("---------------Test " + str(num_times_tested) + "----------------")

    opponents = [Dummy_Opponent(), Buy_Only_Treasure_Opponent()]

    for opponent in opponents:
        for test_kingdom in test_kingdoms:
            player_won, test_num_turns, player_vp, opp_vp = base.test_agent(opponent, test_kingdom, test_output_full_file)

            num_won += player_won
            num_total_turns += test_num_turns
            num_total_player_vp += player_vp
            num_total_opp_vp += opp_vp

    win_percent = num_won / (len(test_kingdoms) * len(opponents))
    avg_num_turns = num_total_turns / (len(test_kingdoms) * len(opponents))
    avg_player_vp = num_total_player_vp / (len(test_kingdoms) * len(opponents))
    avg_opp_vp = num_total_opp_vp / (len(test_kingdoms) * len(opponents))

    print("Agent won", win_percent, ", took average of", avg_num_turns, "turns with avg VP score of", avg_player_vp, "and opp VP score of", avg_opp_vp)
    test_output_file.write(str(num_times_tested) + "\t" + str(num_won) + '\t' + str(win_percent) + '\t'
                           + str(num_total_turns) + "\t" + str(avg_num_turns) + "\t"
                           + str(num_total_player_vp) + "\t" + str(avg_player_vp) + "\t"
                           + str(num_total_opp_vp) + "\t" + str(avg_opp_vp) + "\n")
    test_output_file.flush()

    return win_percent, avg_player_vp - avg_opp_vp


if __name__ == '__main__':
    # Set random seeds
    random.seed(time.time())
    torch.manual_seed(time.time())

    # Make the kingdoms
    train_kingdoms = []
    for i in range(params.num_train_kingdoms):
        train_kingdoms.append(dominion_utils.generate_kingdom())
    test_kingdoms = []
    for i in range(params.num_test_kingdoms):
        test_kingdoms.append(dominion_utils.generate_kingdom())
    val_kingdoms = []
    for i in range(params.num_val_kingdoms):
        val_kingdoms.append(dominion_utils.generate_kingdom())

    # Identifying id for this run
    model_id = random.randint(0, 1000000000)
    print("model_id", model_id)

    # Open files for output
    output_filename = "training/results/" + str(model_id) + '_training.txt'
    loss_filename = "training/results/" + str(model_id) + "_loss.txt"
    test_output_filename = "training/results/" + str(model_id) + "_test.txt"
    test_output_full_filename = "training/results/" + str(model_id) + "_test_full.txt"
    val_output_filename = "training/results/" + str(model_id) + "_val.txt"
    val_output_full_filename = "training/results/" + str(model_id) + "_val_full.txt"
    output_file = open(output_filename, "w+")
    loss_file = open(loss_filename, "w+")
    test_file = open(test_output_filename, "w+")
    test_full_file = open(test_output_full_filename, "w+")
    val_file = open(val_output_filename, "w+")
    val_full_file = open(val_output_full_filename, "w+")

    loss_file.write('Num Times Trained' + '\t' + 'Loss Per Sample' + '\n')
    loss_file.flush()

    # Make agent and base
    agent = Dominion_Agent(loss_file)
    # base = RL_base(agent)
    base = RL_DAgger(agent)

    # Counter variables
    i = 0
    total_time = 0
    total_num_turns = 0

    # Print header
    header = "Kingdom\tOpponent\tLearning Rate\tTau\tPlayer Won\tOpponent VP\tPlayer VP\tRuntime"
    print(header)
    output_file.write(header+'\n')

    parameters_output_filename = "training/results/" + str(model_id) + "_parameters.txt"
    parameters_file = open(parameters_output_filename, "w+")
    params.print_params(parameters_file)

    # Print training and test kingdoms used
    parameters_file.write("\nTraining Kingdoms\n")
    for kingdom in train_kingdoms:
        parameters_file.write(str(kingdom) + "\n")
    parameters_file.write("\nTest Kingdoms\n")
    for kingdom in test_kingdoms:
        parameters_file.write(str(kingdom) + "\n")
    parameters_file.flush()

    test_header = "Num Test\tNum Won\tWin Percent\tNum Total Turns\tAvg Num Turns\tTotal Agent VP\tAvg Agent VP\tTotal Opponent VP\tAvg Opponent VP\n"
    test_file.write(test_header)
    val_file.write(test_header)
    test_file.flush()
    val_file.flush()

    test_full_header = "Turn\tCoins\tCard Purchased\n"
    test_full_file.write(test_full_header)
    val_full_file.write(test_full_header)

    val_results = []
    num_times_tested = 0

    agent.save_model("training/results/" + str(model_id) + "_val_init.pth.tar")
    test_model(val_file, val_full_file, base, val_kingdoms, -1, True)

    for epoch in range(params.num_epochs):
        i = 0
        print('---------------Epoch ' + str(epoch) + '------------------------')

        # Shuffle training data
        random.shuffle(train_kingdoms)

        for kingdom in train_kingdoms:
            if random.random() < 0.2:
                opponent = Buy_Only_Treasure_Opponent()
            else:
                opponent = Dummy_Opponent()

            # Run the agent on kingdom against opponent
            start = time.perf_counter()
            base.reinforcement_loop(opponent, kingdom)
            end = time.perf_counter()

            total_time += (end - start)

            # if want > 1 training iteration, need to save num times won, vp over multiple iterations in base
            assert params.num_training_iterations == 1

            player_vp = agent.num_victory_points()
            opp_vp = opponent.num_victory_points()

            result_text = "%s\t%s\t%f\t%f\t%d\t%d\t%d\t%f" % (str(kingdom), opponent.name, base.learning_rate, base.tau, player_vp > opp_vp, opp_vp, player_vp, end - start)
            if params.debug_mode >= 1:
                print(i, result_text)
            output_file.write(result_text + '\n')
            output_file.flush()

            i += 1

        # test on validation data after each epoch
        if epoch % params.test_on_val_every_epochs == 0:
            agent.save_model("training/results/" + str(model_id) + "_val_" + str(num_times_tested) + '.pth.tar')
            win_percent, avg_vp_diff = test_model(val_file, val_full_file, base, val_kingdoms, num_times_tested, True)
            val_results.append((win_percent,avg_vp_diff))
            num_times_tested += 1

    print('----------------------Training Done------------------------------')
    print("Validation results:", val_results)
    best_model = -1
    best_win_percent = -1
    best_vp_diff = -99999
    i = 0
    for (win_percent, avg_vp_diff) in val_results:
        if (win_percent > best_win_percent) or (win_percent == best_win_percent and avg_vp_diff > best_vp_diff):
            best_model = i
            best_win_percent = win_percent
            best_vp_diff = avg_vp_diff
        i += 1

    assert best_model != -1
    print("Best model:", best_model)

    # load and test best model 10x
    agent.load_model("training/results/" +str(model_id) + "_val_" + str(best_model) + '.pth.tar')
    for t in range(10):
        test_model(test_file, test_full_file, base, test_kingdoms, "final_" + str(t), False)

    # Close files
    output_file.close()
    loss_file.close()
    test_file.close()
    test_full_file.close()
    val_file.close()
    val_full_file.close()
    parameters_file.close()

    print("Total Time to Train: %f" % total_time)
    print("Average Time: %f" % (total_time / len(train_kingdoms)))
    print("model id", model_id)