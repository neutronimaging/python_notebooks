import pandas as pd
import numpy as np

from __code.ipywe import fileselector


class WaveFrontDynamics:

    list_of_ascii_files = None
    list_of_data = None

    def __init__(self, working_dir="~/"):
        self.working_dir = working_dir

    def select_data(self):
        self.list_data_widget = fileselector.FileSelectorPanel(instruction='select list of ascii profile data ...',
                                                               start_dir=self.working_dir,
                                                               next=self.load_data,
                                                               filters={"ASCII": "*.txt"},
                                                               default_filter="ASCII",
                                                               multiple=True)
        self.list_data_widget.show()

    def load_data(self, list_of_ascii_files=None):
        if list_of_ascii_files is None:
            return

        list_of_ascii_files.sort()
        self.list_of_ascii_files = list_of_ascii_files
        list_of_data = []
        for _file in list_of_ascii_files:
            _data = pd.read_csv(_file,
                                skiprows=5,
                                delimiter=",",
                                names=['pixel', 'mean counts'],
                                dtype=np.float,
                                index_col=0)
            list_of_data.append(_data)
        self.list_of_data = list_of_data

    