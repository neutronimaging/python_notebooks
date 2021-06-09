from qtpy.QtWidgets import QDialog
import os

from __code import load_ui


class AdvancedTableHandler(QDialog):

    def __init__(self, parent=None):
        self.parent = parent

        super(AdvancedTableHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_images_advanced_table.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        # initialization
        o_init = Initialization(parent=self,
                                top_parent=self.parent)
        o_init.list_of_metadata()

    def add_metadata(self):
        pass

    def remove_metadata(self):
        pass

    def cancel_clicked(self):
        self.close()

    def ok_clicked(self):
        pass


class Initialization:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def list_of_metadata(self):
        list_of_metadata = self.top_parent.raw_list_metadata
        self.parent.ui.list_metadata_comboBox.addItems(list_of_metadata)
