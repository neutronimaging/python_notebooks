from qtpy.QtWidgets import QFileDialog, QApplication
import os


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        working_dir = os.path.abspath(os.path.dirname(self.parent.working_dir))
        export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         caption="Select folder",
                                                         directory=working_dir)

        print(f"export_folder: {export_folder}")

        if export_folder:
            print("continue")
            