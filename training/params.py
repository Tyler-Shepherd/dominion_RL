import datetime

debug_mode = 0

checkpoint_filename = "C:\\Users\shepht2\Documents\Computer Science\Dominion\dominion_RL\\training\\results\\1-15-19\899647092_val_14.pth.tar"

num_train_kingdoms = 80
num_test_kingdoms = 20
num_val_kingdoms = 20

num_epochs = 1000
num_training_iterations = 1
test_on_val_every_epochs = 50

learning_rate = 0.1

f_learning_rate_decay = 0
learning_rate_start = 0.4
learning_rate_end = 0.0001
learning_rate_decay = 200000

discount_factor = 0.95

# Boltzmann Exploration Parameters
tau_start = 1.0
tau_end = 0.05
tau_decay = 1000000

# Updates every x experience replay trainings
update_target_network_every = 2

# Experience Replay Parameters
train_from_experiences_every_iterations = 40

buffer_size = 500
unusual_sample_factor = 0.9
batch_size = 50

D_in = 6
H = 10
D_out = 1


# Print parameters
def print_params(parameters_file):
    parameters_file.write("num_train_kingdoms\t" + str(num_train_kingdoms) + '\n')
    parameters_file.write("num_test_kingdoms\t" + str(num_test_kingdoms) + '\n')
    parameters_file.write("num_val_kingdoms\t" + str(num_val_kingdoms) + '\n')

    parameters_file.write("num_epochs\t" + str(num_epochs) + '\n')
    parameters_file.write("num_training_iterations\t" + str(num_training_iterations) + '\n')

    if not f_learning_rate_decay:
        parameters_file.write("Learning Rate\t" + str(learning_rate) + '\n')
    else:
        parameters_file.write("Learning Rate Start\t" + str(learning_rate_start) + '\n')
        parameters_file.write("Learning Rate End\t" + str(learning_rate_end) + '\n')
        parameters_file.write("Learning Rate Decay Rate\t" + str(learning_rate_decay) + '\n')

    parameters_file.write("discount_factor\t" + str(discount_factor) + '\n')

    parameters_file.write("tau_start\t" + str(tau_start) + '\n')
    parameters_file.write("tau_end\t" + str(tau_end) + '\n')
    parameters_file.write("tau_decay\t" + str(tau_decay) + '\n')

    parameters_file.write("update_target_network_every\t" + str(update_target_network_every) + '\n')

    parameters_file.write("train_from_experiences_every_iterations\t" + str(train_from_experiences_every_iterations) + '\n')
    parameters_file.write("buffer_size\t" + str(buffer_size) + '\n')
    parameters_file.write("unusual_sample_factor\t" + str(unusual_sample_factor) + '\n')
    parameters_file.write("batch_size\t" + str(batch_size) + '\n')

    parameters_file.write("D_in\t" + str(D_in) + '\n')
    parameters_file.write("H\t" + str(H) + '\n')
    parameters_file.write("D_out\t" + str(D_out) + '\n')

    parameters_file.write("Date\t" + str(datetime.datetime.now()) + '\n')

    parameters_file.flush()