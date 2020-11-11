import os


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_combobox_folder_selected(self):
        return os.path.basename(self.parent.ui.list_folders_combobox.currentText())

    def get_combobox_full_name_folder_selected(self):
        return self.parent.ui.list_folders_combobox.currentText()
