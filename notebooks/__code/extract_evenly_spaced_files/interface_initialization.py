import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QProgressBar
from qtpy import QtGui


class InterfaceInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.splitters()
        self.widgets()
        self.pyqtgraph()
        self.statusbar()

    def splitters(self):
        self.parent.ui.horizontal_splitter.setSizes([200, 800])
        self.parent.ui.vertical_splitter.setSizes([40, 60])

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.image_widget.setLayout(vertical_layout)

        self.parent.ui.statistics_plot = pg.PlotWidget(title="Statistics")
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(self.parent.ui.statistics_plot)
        self.parent.ui.statistics_widget.setLayout(profile_layout)

    def widgets(self):
        self.parent.ui.list_of_files_listWidget.blockSignals(True)
        base_list_of_files_to_extract = self.parent.basename_list_of_files_that_will_be_extracted
        self.parent.ui.list_of_files_listWidget.addItems(base_list_of_files_to_extract)
        self.parent.ui.list_of_files_listWidget.blockSignals(False)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
