import os
from qtpy.QtWidgets import QFileDialog

from __code._utilities.parent import Parent


class Export(Parent):

    def run(self):
        parent_working_dir = os.path.dirname(self.parent.working_dir)
        output_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         directory=parent_working_dir,
                                                         caption="Select where to export the data ...",
                                                         options=QFileDialog.ShowDirsOnly)
        if output_folder:

            print(f"output_folder: {output_folder}")
