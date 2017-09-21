import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os

from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display

import ipywe.fileselector
from NeuNorm.normalization import Normalization
from NeuNorm.roi import ROI

from __code import utilities, file_handler


class NormalizationHandler(object):

    working_dir = ''

    list_images_ui = {'sample': None,
                      'ob': None,
                      'df': None}

    data = {'sample': [],
            'ob': [],
            'df': []}

    integrated_sample = []

    list_file_names = {'sample': [],
                       'ob': [],
                       'df': []}

    o_norm = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.output_folder_ui = None
        self.normalized_data_array = []
        self.roi_selection = None

    def select_images(self, data_type='sample'):
        _instruction = 'Select {} images'.format(data_type)
        self.list_images_ui[data_type] = ipywe.fileselector.FileSelectorPanel(instruction=_instruction,
                                                                              start_dir=self.working_dir,
                                                                              multiple=True)
        self.list_images_ui[data_type].show()

    def get_list_images(self, data_type='sample'):
        return self.list_images_ui[data_type].selected

    def load_data_type(self, data_type='sample'):
        if not (self.list_images_ui[data_type] is None):
            list_images = self.get_list_images(data_type=data_type)
            self.list_file_names[data_type] = list_images
            self.o_norm.load(file=list_images, data_type=data_type, notebook=True)
            self.data[data_type] = self.o_norm.data[data_type]['data']

    def load_data(self):
        self.o_norm = Normalization()

        # sample
        self.load_data_type()

        # ob
        self.load_data_type(data_type='ob')

        # df (if any)
        self.load_data_type(data_type='df')

    def plot_images(self, data_type='sample'):

        sample_array = self.data[data_type]

        def _plot_images(index):
            _ = plt.figure(num=data_type, figsize=(5, 5))
            ax_img = plt.subplot(111)
            ax_img.imshow(sample_array[index], cmap='viridis')

        _ = interact(_plot_images,
                     index=widgets.IntSlider(min=0,
                                             max=len(self.list_file_names[data_type]) - 1,
                                             step=1,
                                             value=0,
                                             description='{} Index'.format(data_type),
                                             continuous_update=False))

    def calculate_integrated_sample(self):
        if len(self.data['sample']) > 1:
            integrated_array = np.array([_array for _array in self.data['sample']])
            self.integrated_sample = integrated_array.mean(axis=0)
        else:
            self.integrated_sample = np.squeeze(self.data['sample'])

    def select_sample_roi(self):

        if self.integrated_sample == []:
            self.calculate_integrated_sample()

        _integrated_sample = self.integrated_sample
        [height, width] = np.shape(_integrated_sample)

        def plot_roi(x_left, y_top, width, height):
            _ = plt.figure(figsize=(5, 5))
            ax_img = plt.subplot(111)
            ax_img.imshow(_integrated_sample,
                          cmap='viridis',
                          interpolation=None)

            _rectangle = patches.Rectangle((x_left, y_top),
                                           width,
                                           height,
                                           edgecolor='white',
                                           linewidth=2,
                                           fill=False)
            ax_img.add_patch(_rectangle)

            return [x_left, y_top, width, height]

        self.roi_selection = interact(plot_roi,
                                      x_left=widgets.IntSlider(min=0,
                                                               max=width,
                                                               step=1,
                                                               value=0,
                                                               description='X Left',
                                                               continuous_update=False),
                                      y_top=widgets.IntSlider(min=0,
                                                              max=height,
                                                              value=0,
                                                              step=1,
                                                              description='Y Top',
                                                              continuous_update=False),
                                      width=widgets.IntSlider(min=0,
                                                              max=width - 1,
                                                              step=1,
                                                              value=60,
                                                              description="Width",
                                                              continuous_update=False),
                                      height=widgets.IntSlider(min=0,
                                                               max=height - 1,
                                                               step=1,
                                                               value=100,
                                                               description='Height',
                                                               continuous_update=False))

    def run_normalization(self):

        [x_left, y_top, width_roi, height_roi] = self.roi_selection.widget.result
        _roi = ROI(x0=x_left, y0=y_top, width=width_roi, height=height_roi)

        self.o_norm.normalization(roi=_roi, notebook=True)

        self.normalized_data_array = self.o_norm.get_normalized_data()

    def select_export_folder(self):

        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder',
                                                                     start_dir=self.working_dir,
                                                                     multiple=False,
                                                                     type='directory')
        self.output_folder_ui.show()

    def export(self):

        output_folder = os.path.abspath(os.path.join(self.output_folder_ui.selected, 'normalization'))
        utilities.make_dir(dir=output_folder)

        w = widgets.IntProgress()
        w.max = len(self.list_file_names['sample'])
        display(w)

        for _index, _file in enumerate(self.list_file_names['sample']):
            basename = os.path.basename(_file)
            _base, _ext = os.path.splitext(basename)
            output_file_name = os.path.join(output_folder, _base + '.tiff')
            file_handler.make_tiff(filename=output_file_name, data=self.normalized_data_array[_index])

            w.value = _index + 1
