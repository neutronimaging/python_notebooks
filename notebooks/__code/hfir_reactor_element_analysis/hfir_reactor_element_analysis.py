import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets.widgets import interact
from ipywidgets import widgets
import numpy as np

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

    def display_data(self):

        x_axis = self.pandas_obj[0]

        def plot(image_index):
            y_axis = self.pandas_obj[image_index]

            figure = plt.figure(figsize=(10, 10))
            ax_img = plt.subplot(111)
            ax_img.plot(x_axis, y_axis)
            ax_img.set_xlabel("Angle (degrees)")
            ax_img.set_ylabel("Average counts")
            plt.show()

        preview = interact(plot,
                           image_index=widgets.IntSlider(min=0,
                                                         max=len(self.column_labels)-2,
                                                         step=1,
                                                         value=0,
                                                         description="Column index",
                                                         continuous_update=False))
