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
                                               layout=widgets.Layout(width='10%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(negative_values, negative_percentage),
                                               layout=widgets.Layout(width='15%'))])

            box4 = widgets.HBox([widgets.Label("Infinite values:",
                                               layout=widgets.Layout(width='10%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(infinite_values, infinite_percentage),
                                               layout=widgets.Layout(width='15%'))])

            box5 = widgets.HBox([widgets.Label("NaN values:",
                                               layout=widgets.Layout(width='10%')),
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
        self.display()

    def display(self):
        data = self.data
        list_files = self.list_files

        def plot_data(index):

            self.fig, [[self.ax0, self.ax1], [self.ax2, self.ax3]] = plt.subplots(ncols=2, nrows=2,
                                                                                  figsize=(15, 10))

            _data = data[index]
            _file = list_files[index]

            # plt.title(os.path.basename(_files[index]))
            cax0 = self.ax0.imshow(_data, cmap='viridis', interpolation=None)
            self.ax0.set_title("Raw Image")
            tmp1 = self.fig.colorbar(cax0, ax=self.ax0)  # colorbar

            self.ax1.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
            self.ax1.set_title("Raw Histogram")

            cax2 = self.ax2.imshow(_data, cmap='viridis', interpolation=None)
            self.ax2.set_title("New Image")
            tmp1 = self.fig.colorbar(cax2, ax=self.ax2)  # colorbar

            self.ax3.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
            self.ax3.set_title("New Histogram")

            self.fig.tight_layout()
            display_ipython.clear_output(wait=True)
            display_ipython.display(plt.gcf())
            display_ipython.clear_output(wait=True)

        tmp3 = widgets.interact(plot_data,
                                index=widgets.IntSlider(min=0,
                                                        max=len(list_files) - 1,
                                                        step=1,
                                                        value=0,
                                                        description='File Index',
                                                        continuous_update=False))


    def neg_on_change(self, change):
        if self.counter == 0:
            _new_index = change['new']['index']
            _list = change['owner'].options
            _new_selection = _list[_new_index]
            self.dropdown_selection = self.dropdown_selection._replace(neg=_new_selection)
            self.counter += 1
            self._refresh_plot()
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
            self._refresh_plot()
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
            self._refresh_plot()
        elif self.counter == 4:
            self.counter = 0
        else:
            self.counter += 1

    def _refresh_plot(self):

        index = 0
        _data = self.data[index]
        _file = self.list_files[index]

        self.fig, [[self.ax0, self.ax1], [self.ax2, self.ax3]] = plt.subplots(ncols=2, nrows=2,
                                                                              figsize=(15, 10))

        # plt.title(os.path.basename(_files[index]))
        cax0 = self.ax0.imshow(_data, cmap='viridis', interpolation=None)
        self.ax0.set_title("Raw Image")
        tmp1 = self.fig.colorbar(cax0, ax=self.ax0)  # colorbar

        self.ax1.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
        self.ax1.set_title("Raw Histogram")

        cax2 = self.ax2.imshow(_data, cmap='viridis', interpolation=None)
        self.ax2.set_title("New Image")
        tmp1 = self.fig.colorbar(cax2, ax=self.ax2)  # colorbar

#        self.ax3.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
        self.ax3.hist(_data.ravel(), range=(0, np.nanmax(_data)), bins=256)
        self.ax3.set_title("New Histogram TESTING")

        self.fig.tight_layout()
        display_ipython.clear_output(wait=True)
        display_ipython.display(plt.gcf())
        display_ipython.clear_output(wait=True)
        self.fix()

    def fix(self):

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

        vertical_box = widgets.VBox([box3, box4, box5])
        display(vertical_box)


    def display_and_correct_images(self):
        data = self.data
        list_files = self.list_files

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


        def give_statistics(index):

            _file = os.path.basename(list_files[index])
            _data = data[index]

            def correct_data(_data=[]):
                global dropdown_selection

                _data = _data.copy()

                # inf
                _result_inf = np.where(np.isinf(_data))
                if dropdown_selection.inf == 'NaN':
                    _data[_result_inf] = np.NaN
                else:
                    _data[_result_inf] = 0

                # nan
                _result_nan = np.where(np.isnan(_data))
                if dropdown_selection.nan == 'NaN':
                    pass
                else:
                    _data[_result_nan] = 0

                # neg
                _result_neg = np.where(_data < 0)
                if dropdown_selection.neg == 'NaN':
                    _data[_result_neg] = np.NaN
                else:
                    _data[_result_neg] = 100

                return _data

            def plot_data():
                _data_corrected = correct_data(_data=_data)

                # plt.title(os.path.basename(_files[index]))
                cax0 = ax0.imshow(_data, cmap='viridis', interpolation=None)
                ax0.set_title("Raw Image")
                tmp1 = fig.colorbar(cax0, ax=ax0)  # colorbar

                ax1.hist(_data.ravel(), range=(np.nanmin(_data), np.nanmax(_data)), bins=256)
                ax1.set_title("Raw Histogram")

                cax2 = ax2.imshow(_data_corrected, cmap='viridis', interpolation=None)
                ax2.set_title("New Image")
                tmp1 = fig.colorbar(cax2, ax=ax2)  # colorbar

                ax3.hist(_data.ravel(), range=(np.nanmin(_data_corrected), np.nanmax(_data_corrected)), bins=256)
                ax3.set_title("New Histogram")

                fig.tight_layout()

            def neg_on_change(change):
                global counter
                global dropdown_selection
                if counter == 0:
                    _new_index = change['new']['index']
                    _list = change['owner'].options
                    _new_selection = _list[_new_index]
                    dropdown_selection = dropdown_selection._replace(neg=_new_selection)
                    plot_data()
                    counter += 1
                elif counter == 4:
                    counter = 0
                else:
                    counter += 1


            def inf_on_change(change):
                global counter
                global dropdown_selection
                if counter == 0:
                    _new_index = change['new']['index']
                    _list = change['owner'].options
                    _new_selection = _list[_new_index]
                    dropdown_selection = dropdown_selection._replace(inf=_new_selection)
                    plot_data()
                    counter += 1
                elif counter == 4:
                    counter = 0
                else:
                    counter += 1

            def nan_on_change(change):
                global counter
                global dropdown_selection
                if counter == 0:
                    _new_index = change['new']['index']
                    _list = change['owner'].options
                    _new_selection = _list[_new_index]
                    dropdown_selection = dropdown_selection._replace(nan=_new_selection)
                    plot_data()
                    counter += 1
                elif counter == 4:
                    counter = 0
                else:
                    counter += 1

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
                                               layout=widgets.Layout(width='10%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(negative_values, negative_percentage),
                                               layout=widgets.Layout(width='15%')),
                                 widgets.Label("to replace by"),
                                 widgets.Dropdown(options=['NaN', '0'],
                                                  value=dropdown_selection.neg)])
            neg_widgets = box3.children[3]
            neg_widgets.observe(neg_on_change)

            box4 = widgets.HBox([widgets.Label("Infinite values:",
                                               layout=widgets.Layout(width='10%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(infinite_values, infinite_percentage),
                                               layout=widgets.Layout(width='15%')),
                                 widgets.Label("to replace by"),
                                 widgets.Dropdown(options=['NaN', '0'],
                                                  value=dropdown_selection.inf)])

            inf_widgets = box4.children[3]
            inf_widgets.observe(inf_on_change)

            box5 = widgets.HBox([widgets.Label("NaN values:",
                                               layout=widgets.Layout(width='10%')),
                                 widgets.Label("{} pixels ({:.3}%)".format(nan_values, nan_percentage),
                                               layout=widgets.Layout(width='15%')),
                                 widgets.Label("to replace by"),
                                 widgets.Dropdown(options=['NaN', '0'],
                                                  value=dropdown_selection.nan)])

            nan_widgets = box5.children[3]
            nan_widgets.observe(nan_on_change)

            vertical_box = widgets.VBox([box1, box2, box3, box4, box5])
            display(vertical_box)

            fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(ncols=2, nrows=2,
                                                         figsize=(15, 10),
                                                         num=os.path.basename(_file))

            plot_data()


        tmp3 = widgets.interact(give_statistics,
                                index=widgets.IntSlider(min=0,
                                                        max=len(list_files) - 1,
                                                        step=1,
                                                        value=0,
                                                        description='File Index',
                                                        continuous_update=False),
                                )














    def export(self):
        output_folder = os.path.abspath(self.list_output_folders_ui.selected)

        base_input_folder = os.path.basename(os.path.dirname(os.path.abspath(self.list_files[0])))
        new_folder_name = base_input_folder + '_cleaned'
        output_folder = os.path.join(output_folder, new_folder_name)
        make_folder(output_folder)

        for _index, _file in enumerate(self.list_files):
            _short_file_name = os.path.basename(_file)
            _full_output_file_name = os.path.join(output_folder, _short_file_name)

            _data = self.clean_data[_index]

            save_data(data=_data, filename=_full_output_file_name)

        display(HTML('<span style="font-size: 20px; color:blue">Files have been created in ' + output_folder + '</span>'))