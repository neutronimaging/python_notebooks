import os
from collections import namedtuple
import numpy as np

from ipywidgets import widgets

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from IPython.core.display import display
from IPython.core.display import HTML

from NeuNorm.normalization import Normalization
from __code.file_folder_browser import FileFolderBrowser
from __code.file_handler import save_data, make_folder

from IPython import display as display_ipython



class FixImages(FileFolderBrowser):

    list_files = []
    data = []
    data_corrected = []
    full_statistics = {}

    fig = None
    ax0 = None
    ax1 = None
    ax2 = None

    counter = 0
    index_image_selected = 0

    Statistics = namedtuple('Statistics',
                            'total_pixels nbr_negative percentage_negative nbr_infinite percentage_infinite nbr_nan percentage_nan')
    DropdownSelection = namedtuple('DropdownSelection', 'neg inf nan')

    dropdown_selection = DropdownSelection(neg='NaN',
                                           inf='NaN',
                                           nan='NaN')

    def __init__(self, working_dir=''):
        super(FixImages, self).__init__(working_dir=working_dir)

    def load(self):

        self.list_files = self.list_images_ui.selected

        data = []

        w = widgets.IntProgress()
        w.max = len(self.list_files)
        display(w)

        for _index, _file in enumerate(self.list_files):

            _o_norm = Normalization()
            _o_norm.load(file=_file)
            _data = _o_norm.data['sample']['data'][0]
            data.append(_data)
            w.value = _index + 1

        self.data = data
        self.data_corrected = data.copy()
        w.close()

    def give_statistics(self):

        data = self.data
        list_files = self.list_files

        def __give_statistics(index):

            def get_statistics_of_roi_cleaned(data):
                _data = data
                _result = np.where(_data < 0)

                nbr_negative = len(_result[0])
                total = np.size(_data)
                percentage_negative = (nbr_negative / total) * 100

                _result_inf = np.where(np.isinf(_data))
                nbr_inf = len(_result_inf[0])
                percentage_inf = (nbr_inf / total) * 100

                nan_values = np.where(np.isnan(_data))
                nbr_nan = len(nan_values[0])
                percentage_nan = (nbr_nan / total) * 100

                stat = self.Statistics(total_pixels=total,
                                       nbr_negative=nbr_negative,
                                       percentage_negative=percentage_negative,
                                       nbr_infinite=nbr_inf,
                                       percentage_infinite=percentage_inf,
                                       nbr_nan=nbr_nan,
                                       percentage_nan=percentage_nan)
                return stat

            _file = os.path.basename(list_files[index])
            _data = data[index]

            stat = get_statistics_of_roi_cleaned(_data)

            number_of_pixels = stat.total_pixels
            negative_values = stat.nbr_negative
            negative_percentage = stat.percentage_negative
            infinite_values = stat.nbr_infinite
            infinite_percentage = stat.percentage_infinite
            nan_values = stat.nbr_nan
            nan_percentage = stat.percentage_nan

            box1 = widgets.HBox([widgets.Label("File Name:"),
                                 widgets.Label(_file,
                                               layout=widgets.Layout(width='80%'))])
            box2 = widgets.HBox([widgets.Label("Total number of pixels:",
                                               layout=widgets.Layout(width='15%')),
                                 widgets.Label(str(number_of_pixels))])

            box3 = widgets.HBox([widgets.Label("Negative values:",
                                               layout=widgets.Layout(width='30%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(negative_values, negative_percentage),
                                               layout=widgets.Layout(width='15%'))])

            box4 = widgets.HBox([widgets.Label("Infinite values:",
                                               layout=widgets.Layout(width='30%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(infinite_values, infinite_percentage),
                                               layout=widgets.Layout(width='15%'))])

            box5 = widgets.HBox([widgets.Label("NaN values:",
                                               layout=widgets.Layout(width='30%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(nan_values, nan_percentage),
                                               layout=widgets.Layout(width='15%'))])

            vertical_box = widgets.VBox([box1, box2, box3, box4, box5])
            display(vertical_box)

        tmp3 = widgets.interact(__give_statistics,
                                index=widgets.IntSlider(min=0,
                                                        max=len(list_files) - 1,
                                                        step=1,
                                                        value=0,
                                                        description='File Index',
                                                        continuous_update=False),
                                )

    def display_and_fix(self):
        self.fix()
        self.correct_data()
        # self.display()
        self.plot()

    def plot(self, refresh=False):

        if refresh:
            self.correct_data()

        index = self.index_image_selected
        _raw_data = self.data[index]
        _data_corrected = self.data_corrected[index]
        _file = self.list_files[index]

        self.fig, [[self.ax0, self.ax1], [self.ax2, self.ax3]] = plt.subplots(ncols=2, nrows=2,
                                                                              figsize=(15, 10))

        # plt.title(os.path.basename(_files[index]))
        cax0 = self.ax0.imshow(_raw_data, cmap='viridis', interpolation=None)
        self.ax0.set_title("Raw Image")
        tmp1 = self.fig.colorbar(cax0, ax=self.ax0)  # colorbar

        histo_error = False
        try:
            self.ax1.hist(_raw_data.ravel(), range=(np.nanmin(_raw_data), np.nanmax(_raw_data)), bins=256)
        except:
            histo_error = True
        self.ax1.set_title("Raw Histogram")

        # corrected data
        cax2 = self.ax2.imshow(_data_corrected, cmap='viridis', interpolation=None)
        self.ax2.set_title("New Image")
        tmp1 = self.fig.colorbar(cax2, ax=self.ax2)  # colorbar

        #        self.ax3.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
        self.ax3.hist(_data_corrected.ravel(),
                      range=(np.nanmin(_data_corrected),
                             np.nanmax(_data_corrected)),
                      bins=256)
        self.ax3.set_title("New Histogram")

        self.fig.tight_layout()

        if refresh:
            display_ipython.clear_output(wait=True)
            display_ipython.display(plt.gcf())
            display_ipython.clear_output(wait=True)

        if histo_error:
            display(HTML(
                '<span style="font-size: 20px; color:red">Histogram of raw images can not be displayed!</span>'))

        if refresh:
            self.fix()

    def neg_on_change(self, change):
        if self.counter == 0:
            _new_index = change['new']['index']
            _list = change['owner'].options
            _new_selection = _list[_new_index]
            self.dropdown_selection = self.dropdown_selection._replace(neg=_new_selection)
            self.counter += 1
            self.plot(refresh=True)
        elif self.counter == 4:
            self.counter = 0
        else:
            self.counter += 1

    def inf_on_change(self, change):
        if self.counter == 0:
            _new_index = change['new']['index']
            _list = change['owner'].options
            _new_selection = _list[_new_index]
            self.dropdown_selection = self.dropdown_selection._replace(inf=_new_selection)
            self.counter += 1
            self.plot(refresh=True)
        elif self.counter == 4:
            self.counter = 0
        else:
            self.counter += 1

    def nan_on_change(self, change):
        if self.counter == 0:
            _new_index = change['new']['index']
            _list = change['owner'].options
            _new_selection = _list[_new_index]
            self.dropdown_selection = self.dropdown_selection._replace(nan=_new_selection)
            self.counter += 1
            self.plot(refresh=True)
        elif self.counter == 4:
            self.counter = 0
        else:
            self.counter += 1

    def index_on_change(self, change):
        if self.counter == 0:
            _new_value = change['new']['value']
            self.counter += 1
            self.index_image_selected = _new_value
            self.plot(refresh=True)
        elif self.counter == 2:
            self.counter = 0
        else:
            self.counter += 1

    def fix(self):

        box2 = widgets.HBox([widgets.Label("File Index:",
                                           layout=widgets.Layout(width='20%')),
                             widgets.IntSlider(value=self.index_image_selected,
                                               max=len(self.list_files)-1,
                                               continuous_update=False,
                                               layout=widgets.Layout(width='20%'))])
        index_slider = box2.children[1]
        index_slider.observe(self.index_on_change)

        box3 = widgets.HBox([widgets.Label("Replace Negative values by",
                                           layout=widgets.Layout(width='20%')),
                             widgets.Dropdown(options=['NaN', '0'],
                                              value=self.dropdown_selection.neg)])

        neg_widget = box3.children[1]
        neg_widget.observe(self.neg_on_change)

        box4 = widgets.HBox([widgets.Label("Replace Infinite values by",
                                           layout=widgets.Layout(width='20%')),
                             widgets.Dropdown(options=['NaN', '0'],
                                              value=self.dropdown_selection.inf)])

        inf_widget = box4.children[1]
        inf_widget.observe(self.inf_on_change)

        box5 = widgets.HBox([widgets.Label("Replace NaN values by",
                                           layout=widgets.Layout(width='20%')),
                             widgets.Dropdown(options=['NaN', '0'],
                                              value=self.dropdown_selection.nan)])

        nan_widget = box5.children[1]
        nan_widget.observe(self.nan_on_change)

        vertical_box = widgets.VBox([box2, box3, box4, box5])
        display(vertical_box)

    def correct_data(self):

        _data = self.data.copy()
        _index = self.index_image_selected

        _data_corrected = _data[_index].copy()

        # inf
        _result_inf = np.where(np.isinf(_data_corrected))
        if self.dropdown_selection.inf == 'NaN':
            _data_corrected[_result_inf] = np.NaN
        else:
            _data_corrected[_result_inf] = 0

        # nan
        _result_nan = np.where(np.isnan(_data_corrected))
        if self.dropdown_selection.nan == 'NaN':
            pass
        else:
            _data_corrected[_result_nan] = 0

        # neg
        _result_neg = np.where(_data_corrected < 0)
        if self.dropdown_selection.neg == 'NaN':
            _data_corrected[_result_neg] = np.NaN
        else:
            _data_corrected[_result_neg] = 0

        _all_data_corrected = self.data_corrected
        _all_data_corrected[_index] = _data_corrected
        self.data_corrected = _all_data_corrected

    def export(self, output_folder):
        base_input_folder = os.path.basename(os.path.dirname(os.path.abspath(self.list_files[0])))
        new_folder_name = base_input_folder + '_cleaned'
        output_folder = os.path.join(output_folder, new_folder_name)
        make_folder(output_folder)

        for _index, _file in enumerate(self.list_files):
            _short_file_name = os.path.basename(_file)
            _full_output_file_name = os.path.join(output_folder, _short_file_name)

            _data = self.data_corrected[_index]

            save_data(data=_data, filename=_full_output_file_name)

        display(HTML('<span style="font-size: 20px; color:blue">Files have been created in ' + output_folder + '</span>'))

    def select_folder_and_export_images(self):
        self.next_function = self.export
        self.select_output_folder()
