import os
from __code.ipywe import fileselector
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.text import Text
from scipy import interpolate
from matplotlib.image import _resample
from matplotlib.transforms import Affine2D

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

    nbr_row = 0
    nbr_column = 0

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
        self.image_height = height
        self.image_width = width

        lambda_2d = np.empty((height, width))
        lambda_2d[:] = np.nan
        compact_lambda_2d = np.empty((self.nbr_row, self.nbr_column))

        strain_mapping_2d = np.empty((height, width))
        strain_mapping_2d[:] = np.nan
        compact_strain_mapping = np.empty((self.nbr_row, self.nbr_column))

        d_2d = np.empty((height, width))
        d_2d[:] = np.nan

        top_left_corner_of_roi = [self.image_height, self.image_width]

        for _key in self.bin.keys():
            x0 = self.bin[_key]['x0']
            y0 = self.bin[_key]['y0']
            x1 = self.bin[_key]['x1']
            y1 = self.bin[_key]['y1']
            row_index = self.bin[_key]['row_index']
            column_index = self.bin[_key]['column_index']

            if x0 < top_left_corner_of_roi[1]:
                top_left_corner_of_roi[1] = x0

            if y0 < top_left_corner_of_roi[0]:
                top_left_corner_of_roi[0] = y0

            compact_lambda_2d[row_index, column_index] = self.lambda_hkl[_key]

            lambda_2d[y0: y1, x0: x1] = self.lambda_hkl[_key]
            strain_mapping_2d[y0: y1, x0: x1] = self.strain_mapping[_key]['val']  # to go to microstrain
            compact_strain_mapping[row_index, column_index] = self.strain_mapping[_key]['val']

            d_2d[y0: y1, x0: x1] = self.d[_key]

        self.compact_lambda_2d = compact_lambda_2d
        self.compact_strain_mapping = compact_strain_mapping
        self.top_left_corner_of_roi = top_left_corner_of_roi

        # # let's interpolate
        # X = np.arange(self.nbr_column)
        # Y = np.arange(self.nbr_row)
        # x, y = np.meshgrid(X, Y)
        #
        # f = interpolate.RectBivariateSpline(Y, X, compact_lambda_2d)
        # Xnew = np.arange(width)
        # Ynew = np.arange(height)
        #
        # lambda_2d = f(Xnew, Ynew)
        #
        self.lambda_hkl_2d = lambda_2d
        self.strain_2d = strain_mapping_2d
        self.d_2d = d_2d

    def display(self):
        self.display_lambda()
        self.display_d()
        self.display_microstrain()

    def display_lambda(self):

        fig = plt.figure(figsize=(4, 4), num=u"\u03BB (\u212B)")

        self.ax0 = fig.add_subplot(111)
        self.ax0.imshow(self.integrated_normalized_radiographs,
                                   vmin=0,
                                   vmax=1,
                                   cmap='gray')
        # self.im0 = self.ax0.imshow(self.compact_lambda_2d, cmap='jet', alpha=0.5)

        self.im0 = self.ax0.imshow(self.lambda_hkl_2d, cmap='jet', alpha=0.5)
        self.cb0 = plt.colorbar(self.im0, ax=self.ax0)
        self.ax0.set_title(u"\u03BB (\u212B)")

        minimum = np.nanmin(self.lambda_hkl_2d)
        maximum = np.nanmax(self.lambda_hkl_2d)
        # minimum = np.nanmin(self.compact_lambda_2d)
        # maximum = np.nanmax(self.compact_lambda_2d)
        step = float((maximum - minimum)/NBR_POINTS_IN_SCALE)

        plt.tight_layout()
        # plt.show()

        def plot_lambda(min_value, max_value, colormap):

            if self.cb0:
                self.cb0.remove()

            data = self.lambda_hkl_2d
            # data = self.compact_lambda_2d
            self.ax0.cla()

            self.ax0.imshow(self.integrated_normalized_radiographs,
                            vmin=0,
                            vmax=1,
                            cmap='gray')
            self.im0 = self.ax0.imshow(data,
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
                                                  layout=widgets.Layout(width="300px")))
        display(v)

    def display_d(self):

        fig = plt.figure(figsize=(4, 4), num=u"d")

        self.ax1 = fig.add_subplot(111)
        self.ax1.imshow(self.integrated_normalized_radiographs,
                        vmin=0,
                        vmax=1,
                        cmap='gray')
        # self.im0 = self.ax0.imshow(self.compact_lambda_2d, cmap='jet', alpha=0.5)

        self.im1 = self.ax1.imshow(self.d_2d, cmap='jet', alpha=0.5)
        self.cb1 = plt.colorbar(self.im1, ax=self.ax1)
        self.ax1.set_title(u"d")

        minimum = np.nanmin(self.d_2d)
        maximum = np.nanmax(self.d_2d)
        step = float((maximum - minimum) / NBR_POINTS_IN_SCALE)

        plt.tight_layout()

        # plt.show()

        def plot_d(min_value, max_value, colormap):
            if self.cb1:
                self.cb1.remove()

            data = self.d_2d
            self.ax1.cla()

            self.ax1.imshow(self.integrated_normalized_radiographs,
                            vmin=0,
                            vmax=1,
                            cmap='gray')
            self.im1 = self.ax1.imshow(data,
                                       cmap=colormap,
                                       vmin=min_value,
                                       vmax=max_value)
            self.cb1 = plt.colorbar(self.im1, ax=self.ax1)

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
                                                  layout=widgets.Layout(width="300px")))
        display(v)

    def display_microstrain(self):
        fig = plt.figure(figsize=(4, 4), num=u"microstrain")

        self.ax2 = fig.add_subplot(111)
        self.ax2.imshow(self.integrated_normalized_radiographs,
                        vmin=0,
                        vmax=1,
                        cmap='gray')

        self.im2 = self.ax2.imshow(self.strain_2d, cmap='jet', alpha=0.5)
        self.cb2 = plt.colorbar(self.im2, ax=self.ax2)
        self.ax2.set_title(u"microstrain")

        minimum = np.nanmin(self.strain_2d)
        maximum = np.nanmax(self.strain_2d)
        step = float((maximum - minimum) / NBR_POINTS_IN_SCALE)

        plt.tight_layout()

        def plot_strain(min_value, max_value, colormap):
            if self.cb2:
                self.cb2.remove()

            data = self.strain_2d
            self.ax2.cla()

            self.ax2.imshow(self.integrated_normalized_radiographs,
                            vmin=0,
                            vmax=1,
                            cmap='gray')
            self.im2 = self.ax2.imshow(data,
                                       cmap=colormap,
                                       vmin=min_value,
                                       vmax=max_value)
            self.cb2 = plt.colorbar(self.im2, ax=self.ax2)

        v = interactive(plot_strain,
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
                                                  layout=widgets.Layout(width="300px")))
        display(v)

    def display_with_interpolation(self):
        self.display_microstrain_with_interpolation()
        # self.display_lambda_with_interpolation()

    def display_lambda_with_interpolation(self):
        data = self.compact_lambda_2d
        grid = np.array(data)
        index = np.isnan(grid)
        # grid[index] = 0

        scale_factor = self.bin_size
        out_dimensions = (grid.shape[0] * scale_factor, grid.shape[1] * scale_factor)

        fig, axs = plt.subplots(nrows=3, num='lambda interpolated', figsize=[5,15])

        transform = Affine2D().scale(scale_factor, scale_factor)
        # Have to get an image to be able to resample
        # Resample takes an _ImageBase or subclass, which require an Axes
        # img = axs[0].imshow(grid, interpolation='spline36', cmap='viridis')
        img = axs[0].imshow(grid, cmap='viridis')
        axs[0].imshow(grid, cmap='viridis')

        img1 = axs[1].imshow(grid, interpolation='gaussian', cmap='viridis')
        interpolated = _resample(img1, grid, out_dimensions, transform=transform)

        # axs[2].imshow(integrated_image, vmin=0, vmax=1, cmap='gray')
        axs[2].imshow(interpolated, cmap='viridis')

    def display_microstrain_with_interpolation(self):
        data = self.compact_strain_mapping
        grid = np.array(data)
        index = np.isnan(grid)
        # grid[index] = 0

        scale_factor = self.bin_size
        out_dimensions = (grid.shape[0] * scale_factor, grid.shape[1] * scale_factor)

        fig1, axs = plt.subplots(nrows=4, num='microstrain interpolated', figsize=[5, 20])

        transform = Affine2D().scale(scale_factor, scale_factor)
        # Have to get an image to be able to resample

        img = axs[0].imshow(grid, cmap='viridis')
        axs[0].imshow(grid, cmap='viridis')

        img1 = axs[1].imshow(grid, interpolation='gaussian', cmap='viridis')
        interpolated = _resample(img1, grid, out_dimensions, transform=transform)

        # axs[2].imshow(integrated_image, vmin=0, vmax=1, cmap='gray')
        axs[2].imshow(interpolated, cmap='viridis')

        # with overlap
        interpolated_strain_mapping_2d = np.empty((self.image_height, self.image_width))
        interpolated_strain_mapping_2d[:] = np.nan

        [y0, x0] = self.top_left_corner_of_roi

        inter_height, inter_width = np.shape(interpolated)
        interpolated_strain_mapping_2d[y0: y0+inter_height, x0: x0+inter_width] = interpolated

        # plt.show()

        # fig1 = plt.figure(num='microstrain', figsize=(6, 6))
        # ax1 = fig1.add_subplot(111)
        axs[3].imshow(self.integrated_normalized_radiographs,
                      vmin=0,
                      vmax=1,
                      cmap='gray')
        im = axs[3].imshow(interpolated_strain_mapping_2d, interpolation='gaussian')
        self.cb = plt.colorbar(im, ax=axs[3])

        minimum = np.nanmin(interpolated_strain_mapping_2d)
        maximum = np.nanmax(interpolated_strain_mapping_2d)
        step = float((maximum - minimum) / NBR_POINTS_IN_SCALE)

        # plt.tight_layout()
        plt.show()

        def plot_interpolated(min_value, max_value, colormap, interpolation_method):

            img = axs[0].imshow(grid, cmap=colormap)
            axs[0].imshow(grid, cmap=colormap)

            axs[1].cla()
            img1 = axs[1].imshow(grid, interpolation=interpolation_method, cmap=colormap)
            interpolated = _resample(img1, grid, out_dimensions, transform=transform)

            axs[2].cla()
            axs[2].imshow(interpolated, vmin=min_value, vmax=max_value, cmap=colormap)

            # with overlap
            interpolated_strain_mapping_2d = np.empty((self.image_height, self.image_width))
            interpolated_strain_mapping_2d[:] = np.nan

            [y0, x0] = self.top_left_corner_of_roi

            inter_height, inter_width = np.shape(interpolated)
            interpolated_strain_mapping_2d[y0: y0 + inter_height, x0: x0 + inter_width] = interpolated

            if self.cb:
                self.cb.remove()

            axs[3].cla()
            axs[3].imshow(self.integrated_normalized_radiographs,
                          vmin=0,
                          vmax=1,
                          cmap='gray')
            im = axs[3].imshow(interpolated_strain_mapping_2d*1e6,
                               interpolation=interpolation_method,
                               cmap=colormap,
                               vmin=min_value*1e6,
                               vmax=max_value*1e6)
            self.cb = plt.colorbar(im, ax=axs[3])

        v = interactive(plot_interpolated,
                        min_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=minimum,
                                                      step=step,
                                                      description='min (x1e6)'),
                        max_value=widgets.FloatSlider(min=minimum,
                                                      max=maximum,
                                                      value=maximum,
                                                      step=step,
                                                      description='min (x1e6)'),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))

        display(v)
