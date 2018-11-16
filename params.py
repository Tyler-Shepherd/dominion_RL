import datetime

debug_mode = 0
print_loss_every = 1

num_epochs = 1
num_training_iterations = 1

learning_rate = 0.04
discount_factor = 0.95
exploration_rate = 0.4

D_in = 6
H = 10
D_out = 1


# Print parameters
def print_params(parameters_file):
    parameters_file.write("print_loss_every\t" + str(print_loss_every) + '\n')
    parameters_file.write("num_epochs\t" + str(num_epochs) + '\n')
    parameters_file.write("num_training_iterations\t" + str(num_training_iterations) + '\n')

    parameters_file.write("learning_rate\t" + str(learning_rate) + '\n')
    parameters_file.write("discount_factor\t" + str(discount_factor) + '\n')
    parameters_file.write("exploration_rate\t" + str(exploration_rate) + '\n')

    parameters_file.write("D_in\t" + str(D_in) + '\n')
    parameters_file.write("H\t" + str(H) + '\n')
    parameters_file.write("D_out\t" + str(D_out) + '\n')

    parameters_file.write("Date\t" + str(datetime.datetime.now()) + '\n')

    parameters_file.flush()