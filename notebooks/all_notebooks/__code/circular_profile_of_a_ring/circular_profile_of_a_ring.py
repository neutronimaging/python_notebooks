import glob
from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector


class CircularProfileOfARing:

    o_norm = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        list_folder_widget = fileselector.FileSelectorPanel(instruction='select input folder ...',
                                                            start_dir=self.working_dir,
                                                            type='directory',
                                                            next=self.folder_selected,
                                                            multiple=False)
        list_folder_widget.show()

    def folder_selected(self, folder_selected):
        list_files = glob.glob(folder_selected + '/*.tif*')
        list_files.sort()
        self.load_data(list_files=list_files)

    def load_data(self, list_files=None):
        o_norm = Normalization()
        o_norm.load(file=list_files, notebook=True)
        self.o_norm = o_norm
