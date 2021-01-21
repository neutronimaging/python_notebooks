from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication

from __code._utilities.table_handler import TableHandler


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def widgets(self):
        # list of files table
        list_high_reso_files = self.parent.o_norm_high_reso.data['sample']['file_name']
        list_low_reso_files = self.parent.o_norm_low_reso.data['sample']['file_name']

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
