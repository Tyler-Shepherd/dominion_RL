import datetime

debug_mode = 3
max_card_id = 13

checkpoint_filename = "../training/results/142489282_val_init.pth.tar"

num_train_kingdoms = 80
num_test_kingdoms = 20
num_val_kingdoms = 20

num_epochs = 10000              # Num times to iterate over all training kingdoms
num_training_iterations = 1     # Num times to train on each kingdom
test_on_val_every_epochs = 100  # After how many epochs to test against validation data

learning_rate = 0.0001

f_learning_rate_decay = 0
learning_rate_start = 0.8
learning_rate_end = 0.001
learning_rate_decay = 200000

discount_factor = 0.95

# Boltzmann Exploration Parameters
tau_start = 1.0
tau_end = 0.2
tau_decay = 10000000

# Updates every x experience replay trainings
update_target_network_every = 2

# Experience Replay Parameters
train_from_experiences_every_iterations = 20

buffer_size = 500
unusual_sample_factor = 0.4
batch_size = 100

D_in = 11 + (max_card_id + 2) + (max_card_id + 1) + (max_card_id + 1) + (max_card_id + 1) + 1 + (max_card_id + 1)
H = 64
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