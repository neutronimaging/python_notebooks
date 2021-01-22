import glob
from NeuNorm.normalization import Normalization
import os

from __code.ipywe import fileselector


class OverlayImages:

    o_norm_high_reso = None
    o_norm_low_reso = None

    current_data_type = 'high resolution'

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self, data_type='high resolution'):
        self.current_data_type = data_type
        list_folder_widget = fileselector.FileSelectorPanel(instruction='select folder containing {} '
                                                                        'images!'.format(data_type),
                                                            start_dir=self.working_dir,
                                                            type='directory',
                                                            next=self.folder_selected,
                                                            multiple=False)
        list_folder_widget.show()

    def folder_selected(self, folder_selected):
        self.working_dir = os.path.dirname(folder_selected)
        list_files = glob.glob(folder_selected + '/*.tif*')
        list_files.sort()
        self.load_data(list_files=list_files, data_type=self.current_data_type)

    def load_data(self, list_files=None, data_type='high resolution'):
        o_norm = Normalization()
        o_norm.load(file=list_files, notebook=True)
        if data_type == 'high resolution':
            self.o_norm_high_res = o_norm
        else:
            self.o_norm_low_res = o_norm
