from __code.wave_front_dynamics.algorithms import ListAlgorithm

MAX_BIN_SIZE = 100
INIT_BIN_SIZE = 1

algorithms_colors = {ListAlgorithm.sliding_average: 'red',
                     ListAlgorithm.change_point: 'green',
                     ListAlgorithm.error_function: 'blue'}

algorithms_symbol = {ListAlgorithm.sliding_average: '*',
                     ListAlgorithm.change_point: '+',
                     ListAlgorithm.error_function: '.'}

