class CalculateProfilesDifference:

    # {'horizontal': {'profiles': {'0': {'xaxis': None, 'profile': None},
    #                              '1': {'xaxis': None, 'profile': None},
    #                              ..., },
    #                 'x0': 0,
    #                 'y0': 0,
    #                 'width': None,
    #                 'length': None,
    #                 'max_width': 50,
    #                 'min_width': 1
    #                 'max_length': 500,
    #                 'min_length': 10,
    #                 'color': <PyQt5.QtGui.QColor ...,
    #                 'color-peak': (255, 0, 0),
    #                 'yaxis': [],
    #                },
    #   ....
    #  'vertical': 'profiles': {'0': {'xaxis': None, 'profile': None},
    #                           '1': {'xaxis': None, 'profile': None},
    #   ....
    #  }
    roi = None

    def __init__(self, parent=None):
        self.parent = parent
        self.roi = self.parent.roi

    def run(self):
        print(self.roi)