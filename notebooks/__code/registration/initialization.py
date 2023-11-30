import pyqtgraph as pg
from pyqtgraph.dockarea import *
from qtpy.QtWidgets import QVBoxLayout, QProgressBar

from __code.icons import icons_rc  # do not remove
from __code._utilities.color import Color
from __code.registration.marker_default_settings import MarkerDefaultSettings


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.pyqtgrpah()
        self.widgets()
        self.table()
        self.parameters()
        self.statusbar()
        self.splitter()

    def splitter(self):
        self.parent.ui.splitter_2.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter_2.setHandleWidth(15)

        self.parent.ui.splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter.setHandleWidth(15)

    def pyqtgrpah(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(400, 600))
        d2 = Dock("Profile", size=(400, 200))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        # registered image
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        # profile selection tool
        self.parent.ui.profile_line = pg.LineSegmentROI([[50, 50], [100, 100]], pen='r')
        self.parent.ui.image_view.addItem(self.parent.ui.profile_line)
        d1.addWidget(self.parent.ui.image_view)
        self.parent.ui.profile_line.sigRegionChanged.connect(self.parent.profile_line_moved)

        # profile
        self.parent.ui.profile = pg.PlotWidget(title='Profile')
        self.parent.ui.profile.plot()
        self.parent.legend = self.parent.ui.profile.addLegend()
        d2.addWidget(self.parent.ui.profile)

        # set up layout
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(area)

        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def widgets(self):
        """size and label of any widgets"""
        self.parent.ui.splitter_2.setSizes([800, 100])

        # update size of table columns
        nbr_columns = self.parent.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.tableWidget.setColumnWidth(_col, self.parent.table_column_width[_col])

        # update slide widget of files
        nbr_files = len(self.parent.data_dict['file_name'])
        self.parent.ui.file_slider.setMinimum(0)
        self.parent.ui.file_slider.setMaximum(nbr_files-1)

        # selected image
        reference_image = self.parent.data_dict['file_name'][0]
        self.parent.ui.reference_image_label.setText(reference_image)

        # selection slider
        self.parent.ui.selection_groupBox.setVisible(False)
        self.parent.ui.next_image_button.setEnabled(True)

        # selected vs reference slider
        self.parent.ui.selection_reference_opacity_groupBox.setVisible(False) # because by default first row = reference selected

    def table(self):
        """populate the table with list of file names and default xoffset, yoffset and rotation"""
        list_file_names = self.parent.data_dict['file_name']
        table_registration = {}

        _row_index = 0
        for _file_index, _file in enumerate(list_file_names):

            _row_infos = {}

            # col 0 - file name
            _row_infos['filename'] = _file
            _row_infos['xoffset'] = 0
            _row_infos['yoffset'] = 0
            _row_infos['rotation'] = 0

            table_registration[_row_index] = _row_infos
            _row_index += 1

        self.parent.table_registration = table_registration
        self.parent.populate_table()

        #select first row
        self.parent.select_row_in_table(0)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(300, 20)
        self.parent.eventProgress.setMaximumSize(300, 20)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def parameters(self):
        nbr_files = len(self.parent.data_dict['file_name'])
        self.parent.nbr_files = nbr_files
        _color = Color()
        self.parent.list_rgb_profile_color = _color.get_list_rgb(nbr_color=nbr_files)

        o_marker = MarkerDefaultSettings(image_reference=self.parent.reference_image)
        self.parent.o_MarkerDefaultSettings = o_marker