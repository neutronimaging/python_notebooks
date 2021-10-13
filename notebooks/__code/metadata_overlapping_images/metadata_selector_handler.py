from qtpy.QtWidgets import QDialog
import os

from __code import load_ui


class MetadataSelectorHandler(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(MetadataSelectorHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_metadata_selector.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.initialization()

    def initialization(self):
        list_metadata = self.parent.raw_list_metadata
        self.ui.select_metadata_combobox.addItems(list_metadata)

    def ok_clicked(self):
        pass
        self.close()

    def cancel_clicked(self):
        self.close()
