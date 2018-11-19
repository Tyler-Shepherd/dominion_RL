import datetime

debug_mode = 3
print_loss_every = 100

num_epochs = 5
num_training_iterations = 1

learning_rate = 0.04

f_learning_rate_decay = 1
learning_rate_start = 0.9
learning_rate_end = 0.01
learning_rate_decay = 20000

discount_factor = 0.95
# exploration_rate = 0.4

# used in boltzmann
tau_start = 1.0
tau_end = 0.05
tau_decay = 1000000

update_target_network_every = 1

D_in = 6
H = 10
D_out = 1


# Print parameters
def print_params(parameters_file):
    parameters_file.write("print_loss_every\t" + str(print_loss_every) + '\n')
    parameters_file.write("num_epochs\t" + str(num_epochs) + '\n')
    parameters_file.write("num_training_iterations\t" + str(num_training_iterations) + '\n')

    if not f_learning_rate_decay:
        parameters_file.write("Learning Rate\t" + str(learning_rate) + '\n')
    else:
        parameters_file.write("Learning Rate Start\t" + str(learning_rate_start) + '\n')
        parameters_file.write("Learning Rate End\t" + str(learning_rate_end) + '\n')
        parameters_file.write("Learning Rate Decay Rate\t" + str(learning_rate_decay) + '\n')

    parameters_file.write("discount_factor\t" + str(discount_factor) + '\n')
    # parameters_file.write("exploration_rate\t" + str(exploration_rate) + '\n')

    parameters_file.write("tau_start\t" + str(tau_start) + '\n')
    parameters_file.write("tau_end\t" + str(tau_end) + '\n')
    parameters_file.write("tau_decay\t" + str(tau_decay) + '\n')

    parameters_file.write("update_target_network_every\t" + str(update_target_network_every) + '\n')

    parameters_file.write("D_in\t" + str(D_in) + '\n')
    parameters_file.write("H\t" + str(H) + '\n')
    parameters_file.write("D_out\t" + str(D_out) + '\n')

    parameters_file.write("Date\t" + str(datetime.datetime.now()) + '\n')

    parameters_file.flush()