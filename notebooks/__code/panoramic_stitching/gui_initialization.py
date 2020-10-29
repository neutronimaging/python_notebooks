import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QProgressBar
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.image_handler import ImageHandler


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def before_loading_data(self):
        self.block_signals(True)
        self.statusbar()
        self.splitter()
        self.pyqtgraph()
        self.matplotlib()
        self.widgets()
        self.table()
        self.block_signals(False)

    def block_signals(self, status):
        list_ui = [self.parent.ui.list_folders_combobox,
                   self.parent.ui.tableWidget]
        for _ui in list_ui:
            _ui.blockSignals(status)

    def splitter(self):
        self.parent.ui.profile_display_splitter.setSizes([500, 500])
        self.parent.ui.display_splitter.setSizes([200, 100])
        self.parent.ui.full_splitter.setSizes([400, 100])

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.stitched_widget.setLayout(image_layout)

    def matplotlib(self):
        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=4, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.horizontal_profile_plot = _matplotlib(parent=self.parent,
                                                          widget=self.parent.ui.horizontal_profile_plot_widget)
        self.parent.kropff_low_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.vertical_profile_plot_widget)

    def widgets(self):
        # list_folders
        list_folders = self.parent.list_folders
        self.parent.ui.list_folders_combobox.addItems(list_folders)

    def table(self):
        column_sizes = [900, 100, 100]
        column_names = ['File name', 'xoffset (px)', 'yoffset (px)']
        o_table = TableHandler(table_ui=self.parent.tableWidget)
        o_table.set_column_sizes(column_sizes=column_sizes)
        o_table.set_column_names(column_names=column_names)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def after_loading_data(self):
        self.parent.list_folder_combobox_value_changed()
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.select_rows(list_of_rows=[0])
