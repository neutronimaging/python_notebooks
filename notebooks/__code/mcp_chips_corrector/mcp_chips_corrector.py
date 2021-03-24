import glob
import os
from IPython.core.display import HTML
from IPython.display import display

from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector


class McpChipsCorrector:

    working_data = None
    sum_img_data = None

    working_list_files = None
    sum_file = None

    def __init__(self, working_dir="./"):
        self.working_dir = working_dir

    def select_folder(self):
        select_data = fileselector.FileSelectorPanel(instruction='Select MCP Folder ...',
                                                     start_dir=self.working_dir,
                                                     next=self.load_data,
                                                     type='directory',
                                                     multiple=False)
        select_data.show()

    def load_data(self, folder_selected):
        full_list_files = glob.glob(os.path.join(folder_selected, '*.fits'))
        full_list_files.sort()

        working_list_files = [file for file in full_list_files if not "_SummedImg.fits" in file]
        summed_img_file = [file for file in full_list_files if "_SummedImg.fits" in file]

        # o_norm = Normalization()
        # o_norm.load(file=working_list_files, notebook=True)
        #
        # self.working_list_files = working_list_files
        # self.working_data = o_norm.data['sample']['data']

        o_norm = Normalization()
        o_norm.load(file=summed_img_file, notebook=True)

        self.sum_file = summed_img_file[0]
        self.sum_img_data = o_norm.data['sample']['data'][0]

        display(HTML('<span style="font-size: 20px; color:blue">' + str(len(working_list_files)+1) + \
                     ' files have been loaded</span>'))
