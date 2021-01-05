import numpy as np
import json
from qtpy.QtWidgets import QFileDialog
import os


class ExportProfiles:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        working_dir = os.path.abspath(os.path.dirname(self.parent.working_dir))
        file_name = QFileDialog.getSaveFileName(self.parent,
                                                caption="Select or define filename ...",
                                                directory=working_dir,
                                                filter="ascii(*.csv)",
                                                initialFilter='ascii')

        if file_name[0]:
            print(f"file_name is {file_name[0]}")
