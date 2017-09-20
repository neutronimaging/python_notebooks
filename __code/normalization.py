import matplotlib.patches as patches
import matplotlib.pyplot as plt

from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML

import ipywe.fileselector
from NeuNorm.normalization import Normalization


class NormalizationHandler(object):

    list_images_ui = {'sample': None,
                   'ob': None,
                   'df': None}

    data = {'sample': [],
            'ob': [],
            'df': []}

    list_file_names = {'sample': [],
                       'ob': [],
                       'df': []}

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_images(self, data_type='sample'):
        _instruction = 'Select {} images'.format(data_type)
        self.list_images_ui[data_type] = ipywe.fileselector.FileSelectorPanel(instruction= _instruction,
                                                                   start_dir= self.working_dir,
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
            fig = plt.figure(figsize=(5, 5))
            ax_img = plt.subplot(111)
            ax_img.imshow(sample_array[index], cmap='viridis')

        preview = interact(_plot_images,
                           index=widgets.IntSlider(min=0,
                                                   max=len(self.list_file_names[data_type]) - 1,
                                                   step=1,
                                                   value=0,
                                                   description='{} Index'.format(data_type),
                                                   continuous_update=False))