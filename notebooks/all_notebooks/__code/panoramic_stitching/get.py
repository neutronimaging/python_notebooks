import os


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_combobox_folder_selected(self):
        return os.path.basename(self.parent.ui.list_folders_combobox.currentText())

