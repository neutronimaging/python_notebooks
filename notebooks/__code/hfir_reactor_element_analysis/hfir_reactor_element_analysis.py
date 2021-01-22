import pandas as pd
import numpy as np
from IPython.core.display import HTML
from IPython.core.display import display, clear_output

from __code.ipywe import fileselector
from __code.file_handler import read_ascii

class HfirReactorElementAnalysis:

    pandas_obj = None

    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    def select_ascii_file(self):
        ascii_file_ui = fileselector.FileSelectorPanel(instruction="Select ASCII file ...",
                                                       start_dir=self.working_dir,
                                                       next=self.load_ascii,
                                                       filters={"CSV": "*.csv"},
                                                       default_filter="CSV")
        ascii_file_ui.show()

    def load_ascii(self, ascii_file_name):

        display(HTML('<span style="font-size: 20px; color:Blue">Loading data set ... PROCESSING!</span>'))

        # retrieving metadata and column names
        ascii_contain = read_ascii(filename=ascii_file_name)
        formatted_ascii_contain = ascii_contain.split("\n")
        for _line_number, _line_contain in enumerate(formatted_ascii_contain):
            if _line_contain == "#":
                break
        metadata = formatted_ascii_contain[:_line_number]
        column_labels = ["Angle (degrees)"]
        for _text in metadata:
            if _text.startswith("# column "):
                part1, part2 = _text.split(":")
                column_labels.append(part2.strip())
        self.column_labels = column_labels

        # retrieving data with pandas
        self.pandas_obj = pd.read_csv(ascii_file_name,
                                      skiprows=_line_number + 2,
                                      delimiter=", ",
                                      names=column_labels,
                                      dtype=np.float,
                                      index_col=0)

        clear_output(wait=False)
        display(HTML('<span style="font-size: 20px; color:green">Loading data set ... DONE!</span>'))
