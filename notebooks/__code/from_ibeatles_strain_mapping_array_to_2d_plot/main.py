import os
from __code.ipywe import fileselector
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.text import Text

INTERPOLATION_METHODS = ['none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                         'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
                         'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']
DEFAULT_INTERPOLATION = 'none'

CMAPS = ['viridis', 'jet']
DEFAULT_CMAPS = 'viridis'

DEFAULT_DATA_TYPE = 'lambda'
NBR_POINTS_IN_SCALE = 100


class Main:

    ascii_filename = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_ascii_file(self):
        self.file_ui = fileselector.FileSelectorPanel(instruction="Select Ascii file",
                                                      start_dir=self.working_dir,
                                                      multiple=False,
                                                      next=self.load)
        self.file_ui.show()

    def load(self, filename):
        self.ascii_filename = filename
        self.import_ascii()
        display(HTML('<span style="font-size: 20px; color:blue">' + str(os.path.basename(filename)) + ' '
                                                                                                  'has been loaded !</span>'))

    def import_ascii(self):
        self.file_object = pd.read_csv(self.ascii_filename, sep=', ')

    def preview_ascii(self):
        print(self.file_object)

    def process_data(self):
        original_x0 = list(self.file_object['bin x0'])
        original_y0 = list(self.file_object['bin y0'])

        list_set_x0 = list(set(original_x0))
        list_set_x0.sort()
        list_set_y0 = list(set(original_y0))
        list_set_y0.sort()

        lambda_2d = np.zeros((len(list_set_y0), len(list_set_x0)))
        strain_2d = np.zeros((len(list_set_y0), len(list_set_x0)))
        d_2d = np.zeros((len(list_set_y0), len(list_set_x0)))

        for _location in np.arange(len(self.file_object)):
            _x0 = self.file_object.iloc[_location]['bin x0']
            _y0 = self.file_object.iloc[_location]['bin y0']
            _x = list_set_x0.index(_x0)
            _y = list_set_y0.index(_y0)

            _lambda = self.file_object.iloc[_location]['lambda hkl val']
            lambda_2d[_y, _x] = _lambda

            _strain = self.file_object.iloc[_location]['strain']
            strain_2d[_y, _x] = _strain

            _d = self.file_object.iloc[_location]['d value']
            d_2d[_y, _x] = _d

        self.data_dict = {'lambda': lambda_2d,
                          'microstrain': strain_2d * 1e6,
                          'd': d_2d}

    def display(self):

        fig, ax = plt.subplots()
        self.im = ax.imshow(self.data_dict[DEFAULT_DATA_TYPE])
        self.cb = plt.colorbar(self.im, ax=ax)
        plt.show()

        self.current_data_type = DEFAULT_DATA_TYPE

        def plot(min_value=0, max_value=0, data_type=None, colormap=None, interpolation_method=None):

            if not (data_type == self.current_data_type):
                min_value = self.scale[data_type]['min_value']
                max_value = self.scale[data_type]['max_value']
                self.current_data_type = data_type
            else:
                self.scale[data_type]['min_value'] = min_value
                self.scale[data_type]['max_value'] = max_value

            self.cb.remove()
            plt.title(f"{data_type}")

            data = self.data_dict[data_type]

            self.im = ax.imshow(data,
                                interpolation=interpolation_method,
                                cmap=colormap,
                                vmin=min_value,
                                vmax=max_value)
            self.cb = plt.colorbar(self.im, ax=ax)

            # adding digit in colorbar scale
            ticks = self.cb.ax.get_yticklabels()

            # for _index, _tick in enumerate(ticks):
            #
            #     (_x, _y) = _tick.get_position()
            #     _text = _tick.get_text()
            #
            #     # trick to fix error with matplotlib '-' that is not the normal negative character
            #     if _text:
            #         if _text[0].encode() == b'\xe2\x88\x92':
            #             _text_fixed = "-" + _text[1:]
            #             _text = _text_fixed
            #
            #         if data_type == 'microstrain':
            #             _new_text = f"{float(_text)}"
            #         else:
            #             _new_text = f"{float(_text):.4f}"
            #
            #     else:
            #         _new_text = _text
            #
            #     ticks[_index] = Text(_x, _y, _new_text)
            #
            # self.cb.ax.set_yticklabels(ticks)

            # adding digits in cursor z value
            numrows, numcols = self.data_dict[data_type].shape
            def format_coord(x, y):
                col = int(x + 0.5)
                row = int(y + 0.5)
                if col >= 0 and col < numcols and row >= 0 and row < numrows:
                    z = self.data_dict[data_type][row, col]
                    return 'x=%d, y=%d, z=%1.4f' % (x, y, z)
                else:
                    return 'x=%d, y=%d' % (x, y)

            ax.format_coord = format_coord

            plt.show()

            minimum = self.scale[data_type]['min']
            maximum = self.scale[data_type]['max']
            step = self.scale[data_type]['step']

            # print(f"{minimum = }")
            # print(f"{maximum = }")
            # print(f"{min_value = }")
            # print(f"{max_value =}")
            # print(f"{step =}")

            try:

                # update min slider
                v.children[0].max = maximum
                v.children[0].min = minimum
                v.children[0].step = step
                v.children[0].value = min_value

                # update max slider
                v.children[1].max = maximum
                v.children[1].min = minimum
                v.children[1].step = step
                v.children[1].value = max_value

            except NameError:
                # print("error generated!")
                return

        self.scale = {'lambda': {'min': np.nanmin(self.data_dict['lambda']),
                                 'max': np.nanmax(self.data_dict['lambda']),
                                 'step': (np.nanmax(self.data_dict['lambda']) -
                                          np.nanmin(self.data_dict['lambda'])) / NBR_POINTS_IN_SCALE,
                                 'min_value': np.nanmin(self.data_dict['lambda']),
                                 'max_value': np.nanmax(self.data_dict['lambda']),
                                 },
                      'd': {'min': np.nanmin(self.data_dict['d']),
                            'max': np.nanmax(self.data_dict['d']),
                            'step': (np.nanmax(self.data_dict['d']) - np.min(self.data_dict['d'])) / NBR_POINTS_IN_SCALE,
                            'min_value': np.nanmin(self.data_dict['d']),
                            'max_value': np.nanmax(self.data_dict['d']),
                            },
                      'microstrain': {'min': np.nanmin(self.data_dict['microstrain']),
                                      'max': np.nanmax(self.data_dict['microstrain']),
                                      'step': (np.nanmax(self.data_dict['microstrain']) -
                                               np.nanmin(self.data_dict['microstrain'])) / NBR_POINTS_IN_SCALE,
                                      'min_value': np.nanmin(self.data_dict['microstrain']),
                                      'max_value': np.nanmax(self.data_dict['microstrain']),
                                      },
                      }

        minimum = self.scale[DEFAULT_DATA_TYPE]['min']
        maximum = self.scale[DEFAULT_DATA_TYPE]['max']
        step = self.scale[DEFAULT_DATA_TYPE]['step']
        min_value = self.scale[DEFAULT_DATA_TYPE]['min_value']
        max_value = self.scale[DEFAULT_DATA_TYPE]['max_value']

        v = interactive(plot,
                        min_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=min_value,
                                                      step=step),
                        max_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=max_value,
                                                      step=step),
                        data_type=widgets.Dropdown(options=['lambda', 'd', 'microstrain'],
                                                   value=DEFAULT_DATA_TYPE,
                                                   layout=widgets.Layout(width="300px")),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))
        display(v)
