"""An encapsulated experiment, containing data and graphing details

    The updated data structure uses OrderedDicts to allow dictionary
    keys to also function as data, simplifying quering the data.

    { 'Experiment #1 Name': {...}, 
      'Experiment #2 Name': {
            'x_label': 'Independent axis label',
            'y_label': 'Dependent axis label',
            'data': {
                'Sample #1 Name': {...},
                'Sample #2 Name': {
                    'x_values': [1, 2, 3],
                    'y_values': [0, 3, 8],
                }
            }
        }
    }

"""

from outlet import ParserRegistry


class Anscombe(ParserRegistry):
    name = 'anscombe'
    description = 'Anscombe Quartet'

    def __call__(self):
        return {
            'show_fit': True,
            'blank_correction': False,
            'x_axis_type': 'linear',
            'curr_function' : 'linear',
            'experiments': {'Anscombe': {
                    'x_axis_label': 'X',
                    'y_axis_label': 'Y',
                    'data': {
                        'Set I': {
                            'x_values': [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
                            'y_values': [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
                        },
                        'Set II': {
                            'x_values': [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
                            'y_values': [9.14, 8.14, 8.74, 8.77, 9.26, 8.1, 6.13, 3.1, 9.13, 7.26, 4.74],
                        },
                        'Set III': {
                            'x_values': [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
                            'y_values': [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
                        },
                        'Set IV': {
                            'x_values': [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
                            'y_values': [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.5, 5.56, 7.91, 6.89],
                        },
                    },
                },
            },
        }
