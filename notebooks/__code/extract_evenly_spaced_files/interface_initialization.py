import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout

class InterfaceInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.splitters()
        self.widgets()
        self.pyqtgraph()

    def splitters(self):
        self.parent.ui.horizontal_splitter.setSizes([200, 800])
        self.parent.ui.vertical_splitter.setSizes([40, 60])

    def pyqtgraph(self):
        self.parent.ui.statistics_plot = pg.PlotWidget(title="Statistics")
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(self.parent.ui.statistics_plot)
        self.parent.ui.statistics_widget.setLayout(profile_layout)

    def widgets(self):
        base_list_of_files_to_extract = self.parent.basename_list_of_files_that_will_be_extracted
        self.parent.ui.list_of_files_listWidget.addItems(base_list_of_files_to_extract)
