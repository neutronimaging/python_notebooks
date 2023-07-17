from IPython.core.display import HTML
from IPython.display import display
from ipywidgets import widgets
import numpy as np

from NeuNorm.normalization import Normalization

# from __code import file_handler
from __code.ipywe import fileselector


class LoadImages:

    nbr_files = 0
    images_dimension = {'height': 0,
                        'width': 0}

    working_data = []
    working_dir = ''
    list_images = []

    # use with virtual array (data are loaded on the fly)
    data_dict = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_images(self, use_next=False, virtual_load=False):

        if virtual_load:
            next = self.prepare_images_array

        else:
            if next is None:
                if use_next:
                    next = self.load_images
                else:
                    next = None

        self.message = widgets.Label('SELECT THE IMAGES YOU WANT TO WORK ON ...')
        display(self.message)

        # display(HTML('<span style="font-size: 20px; color:blue">Select the images you want to work on!</span>'))
        self.list_images_ui = fileselector.FileSelectorPanel(instruction='Select Images...',
                                                             multiple=True,
                                                             next=next,
                                                             start_dir=self.working_dir)
        self.list_images_ui.show()

    def prepare_images_array(self, list_images):
        self.message.close()
        self.list_images = list_images

        self.data_dict = {}
        if list_images == []:
            return

        for index, image in enumerate(list_images):
            self.data_dict[index] = {'filename': image,
                                     'data': None}

    def load_images(self, list_images=[]):
        if list_images == []:
            list_images = self.list_images_ui.selected

        self.o_norm = Normalization()
        self.o_norm.load(file=list_images, notebook=True)

        self.nbr_files = len(list_images)
        [self.images_dimension['height'], self.images_dimension['width']] = \
            np.shape(self.o_norm.data['sample']['data'][0])
        self.working_data = np.squeeze(self.o_norm.data['sample']['data'])
        self.list_images = list_images
