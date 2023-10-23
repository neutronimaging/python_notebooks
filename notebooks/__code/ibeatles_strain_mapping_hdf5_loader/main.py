import os
from __code.ipywe import fileselector
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.text import Text

from __code.ibeatles_strain_mapping_hdf5_loader.hdf5_handler import Hdf5Handler

INTERPOLATION_METHODS = ['none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                         'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
                         'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']
DEFAULT_INTERPOLATION = 'none'

CMAPS = ['viridis', 'jet']
DEFAULT_CMAPS = 'viridis'

DEFAULT_DATA_TYPE = 'lambda'
NBR_POINTS_IN_SCALE = 100


class Main:

    hdf5_filename = None

    integrated_normalized_radiographs = None
    metadata = None

    strain_mapping = None
    d = None
    lambda_hkl = None

    strain_mapping_2d = None
    d_2d = None
    lambda_hkl_2d = None

    cb0 = None
    cb1 = None
    cb2 = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_hdf5_file(self):
        self.file_ui = fileselector.FileSelectorPanel(instruction="Select HDF5 file",
                                                      start_dir=self.working_dir,
                                                      multiple=False,
                                                      filters={'ibeatles hdf5': 'fitting_*.h5'},
                                                      default_filter='ibeatles hdf5',
                                                      next=self.load)
        self.file_ui.show()

    def load(self, filename):
        self.hdf5_filename = filename
        self.import_hdf5()
        display(HTML('<span style="font-size: 20px; color:blue">' + str(os.path.basename(filename)) + ' '
                                                                                                  'has been loaded !</span>'))

    def import_hdf5(self):
        o_import = Hdf5Handler(parent=self)
        o_import.load(filename=self.hdf5_filename)

    def process_data(self):
        # format the data to be able to display them

        [height, width] = np.shape(self.integrated_normalized_radiographs)

        lambda_2d = np.empty((height, width))
        lambda_2d[:] = np.nan

        strain_mapping_2d = np.empty((height, width))
        strain_mapping_2d[:] = np.nan

        d_2d = np.empty((height, width))
        d_2d[:] = np.nan

        for _key in self.bin.keys():

            x0 = self.bin[_key]['x0']
            y0 = self.bin[_key]['y0']
            x1 = self.bin[_key]['x1']
            y1 = self.bin[_key]['y1']

            lambda_2d[y0: y1, x0: x1] = self.lambda_hkl[_key]
            strain_mapping_2d[y0: y1, x0: x1] = self.strain_mapping[_key]['val']
            d_2d = self.d[_key]

        self.lambda_hkl_2d = lambda_2d
        self.strain_2d = strain_mapping_2d
        self.d_2d = d_2d

    def display(self):
        self.display_lambda()
        # self.display_d()
        # self.display_microstrain()

    def display_lambda(self):

        fig = plt.figure(figsize=(4, 4), num=u"\u03BB (\u212B)")

        self.ax0 = fig.add_subplot(111)
        self.ax0.imshow(self.integrated_normalized_radiographs,
                                   vmin=0,
                                   vmax=1,
                                   cmap='gray')
        self.im0 = self.ax0.imshow(self.lambda_hkl_2d, cmap='jet', alpha=0.5)
        self.cb0 = plt.colorbar(self.im0, ax=self.ax0)
        self.ax0.set_title(u"\u03BB (\u212B)")

        minimum = np.nanmin(self.lambda_hkl_2d)
        maximum = np.nanmax(self.lambda_hkl_2d)
        step = float((maximum - minimum)/NBR_POINTS_IN_SCALE)

        plt.tight_layout()
        # plt.show()

        def plot_lambda(min_value, max_value, colormap, interpolation_method):

            if self.cb0:
                self.cb0.remove()

            data = self.lambda_hkl_2d
            self.ax0.cla()

            self.ax0.imshow(self.integrated_normalized_radiographs,
                            vmin=0,
                            vmax=1,
                            cmap='gray')
            self.im0 = self.ax0.imshow(data,
                                       interpolation=interpolation_method,
                                       cmap=colormap,
                                       vmin=min_value,
                                       vmax=max_value)
            self.cb0 = plt.colorbar(self.im0, ax=self.ax0)

        v = interactive(plot_lambda,
                        min_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=minimum,
                                                      step=step),
                        max_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=maximum,
                                                      step=step),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))
        display(v)

    def display_d(self):

        fig = plt.figure(figsize=(4, 4), num='d')

        self.ax1 = fig.add_subplot(111)
        self.im1 = self.ax1.imshow(self.data_dict['d'])
        self.cb1 = plt.colorbar(self.im1, ax=self.ax1)
        self.ax1.set_title("d")

        minimum = np.nanmin(self.data_dict['d'])
        maximum = np.nanmax(self.data_dict['d'])
        step = float((maximum - minimum) / NBR_POINTS_IN_SCALE)

        plt.tight_layout()
        plt.show()

        def plot_d(min_value, max_value, colormap, interpolation_method):

            if self.cb1:
                self.cb1.remove()

            data = self.data_dict['d']
            self.ax1.cla()

            self.im1 = self.ax1.imshow(data,
                                       interpolation=interpolation_method,
                                       cmap=colormap,
                                       vmin=min_value,
                                       vmax=max_value)
            self.cb1 = plt.colorbar(self.im1, ax=self.ax1)

            #adding digit in colorbar scale
            ticks = self.cb1.ax.get_yticklabels()

            for _index, _tick in enumerate(ticks):

                (_x, _y) = _tick.get_position()
                _text = _tick.get_text()

                # trick to fix error with matplotlib '-' that is not the normal negative character
                if _text:
                    if _text[0].encode() == b'\xe2\x88\x92':
                        _text_fixed = "-" + _text[1:]
                        _text = _text_fixed

                    _new_text = f"{float(_text):.4f}"

                else:
                    _new_text = _text

                ticks[_index] = Text(_x, _y, _new_text)

            self.cb1.ax.set_yticklabels(ticks)

        v = interactive(plot_d,
                        min_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=minimum,
                                                      step=step),
                        max_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=maximum,
                                                      step=step),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))
        display(v)

    def display_microstrain(self):
        fig = plt.figure(figsize=(5, 5), num='microstrain')

        self.ax2 = fig.add_subplot(111)
        self.im2 = self.ax2.imshow(self.data_dict['microstrain'])
        self.cb2 = plt.colorbar(self.im2, ax=self.ax2)
        self.ax2.set_title("microstrain")

        minimum = np.nanmin(self.data_dict['microstrain'])
        maximum = np.nanmax(self.data_dict['microstrain'])
        step = float((maximum - minimum) / NBR_POINTS_IN_SCALE)

        plt.tight_layout()
        plt.show()

        def plot_microstrain(min_value, max_value, colormap, interpolation_method):

            if self.cb2:
                self.cb2.remove()

            data = self.data_dict['microstrain']
            self.ax2.cla()

            self.im2 = self.ax2.imshow(data,
                                       interpolation=interpolation_method,
                                       cmap=colormap,
                                       vmin=min_value, 
                                       vmax=max_value)
            self.cb2 = plt.colorbar(self.im2, ax=self.ax2)

            # adding digit in colorbar scale
            ticks = self.cb2.ax.get_yticklabels()

            for _index, _tick in enumerate(ticks):

                (_x, _y) = _tick.get_position()
                _text = _tick.get_text()

                # trick to fix error with matplotlib '-' that is not the normal negative character
                if _text:
                    if _text[0].encode() == b'\xe2\x88\x92':
                        _text_fixed = "-" + _text[1:]
                        _text = _text_fixed

                    _new_text = f"{float(_text)}"

                else:
                    _new_text = _text

                ticks[_index] = Text(_x, _y, _new_text)

            self.cb2.ax.set_yticklabels(ticks)

            # adding digits in cursor z value
            numrows, numcols = data.shape
            def format_coord(x, y):
                col = int(x + 0.5)
                row = int(y + 0.5)
                if col >= 0 and col < numcols and row >= 0 and row < numrows:
                    z = data[row, col]
                    return 'x=%d, y=%d, z=%1.4f microstrain' % (x, y, z)
                else:
                    return 'x=%d, y=%d' % (x, y)

            self.ax2.format_coord = format_coord

        v = interactive(plot_microstrain,
                        min_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=minimum,
                                                      step=step),
                        max_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=maximum,
                                                      step=step),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))
        display(v)
