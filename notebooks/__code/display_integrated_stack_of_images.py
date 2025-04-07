import numpy as np
import matplotlib.pyplot as plt

from NeuNorm.normalization import Normalization
from __code import file_handler
from __code import ipywe

class DisplayIntegratedStackOfImages(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                                    type='directory',
                                                                    start_dir=self.working_dir,
                                                                    multiple=False)
        self.input_folder_ui.show()

    def __retrieve_files(self):
        input_folder = self.input_folder_ui.selected
        list_files = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=input_folder)[0]
        self.list_files = file_handler.remove_file_from_list(list_files=list_files,
                                                             regular_expression='.*_SummedImg.fits')

    def __load(self):
        o_norm = Normalization()
        o_norm.load(file=self.list_files, notebook=True)
        self.stack = o_norm.data['sample']['data']

    def __integrate(self):
        self.integrate_stack = np.array(self.stack).sum(axis=0)

    def __display(self):
        plt.figure()
        plt.imshow(self.integrate_stack)
        plt.colorbar()

    def display_integrated_stack(self):
        self.__retrieve_files()
        self.__load()
        self.__integrate()
        self.__display()

