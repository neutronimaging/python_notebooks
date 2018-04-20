from IPython.core.display import HTML
from IPython.core.display import display

import os
import pyqtgraph as pg
from pyqtgraph.dockarea import *

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_registration_profile import Ui_MainWindow as UiMainWindowProfile



class RegistrationProfileUi(QMainWindow):

    does_top_parent_exist = False

    data_dict = None
    table_column_width = [350, 100, 100, 100, 100]

    # reference file
    reference_image_index = 0
    reference_image = []
    reference_image_short_name = ''
    color_reference_background = QtGui.QColor(50, 250, 50)

    def __init__(self, parent=None, data_dict=None):

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindowProfile()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration Profile Tool")

        self.init_widgets()
        self.init_pyqtgraph()
        self.init_statusbar()

        self.parent = parent
        if parent:
            self.data_dict = self.parent.data_dict
            self.does_top_parent_exist = True
        elif data_dict:
            display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
                (maybe hidden behind this browser!)</span>'))
            self.data_dict = data_dict
        else:
            raise ValueError("please provide data_dict")

        self.init_reference_image()
        self.init_table()

    ## Initialization

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(True)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def init_widgets(self):
        # no need to show save and close if not called from parent UI
        if self.parent is None:
            self.ui.save_and_close_button.setVisible(False)

        # table columns
        self.ui.tableWidget.blockSignals(True)
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])
        self.ui.tableWidget.blockSignals(False)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(600, 600))
        d2 = Dock("Horizontal Profile", size=(300, 200))
        d3 = Dock("Vertical Profile", size=(300, 200))
        d4 = Dock("Peaks Position", size=(600, 600))

        area.addDock(d2, 'top')
        area.addDock(d1, 'left', d2)
        area.addDock(d4, 'above', d1)
        area.addDock(d3, 'bottom', d2)
        #area.moveDock(d1, 'above', d4)

        # registered image ara (left dock)
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        d1.addWidget(self.ui.image_view)

        # horizontal profile area
        self.ui.hori_profile = pg.PlotWidget(title='Horizontal Profile')
        self.ui.hori_profile.plot()
        d2.addWidget(self.ui.hori_profile)

        # vertical profile area
        self.ui.verti_profile = pg.PlotWidget(title='Vertical Profile')
        self.ui.verti_profile.plot()
        d3.addWidget(self.ui.verti_profile)

        # all peaks position
        self.ui.peaks = pg.PlotWidget(title='All Peaks')
        self.ui.peaks.plot()
        d4.addWidget(self.ui.peaks)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def init_reference_image(self):
        if self.does_top_parent_exist:
            self.reference_image_index = self.parent.reference_image_index
            self.reference_image = self.parent.reference_image
            self.reference_image_short_name = self.parent.reference_image_short_name
        else:
            self.reference_image = self.data_dict['data'][self.reference_image_index]
            self.reference_image_short_name = os.path.basename(self.data_dict['file_name'][self.reference_image_index])

    def init_table(self):
        data_dict = self.data_dict
        _list_files = data_dict['file_name']
        _short_list_files = [os.path.basename(_file) for _file in _list_files]

        self.ui.tableWidget.blockSignals(True)
        for _row, _file in enumerate(_short_list_files):
            self.ui.tableWidget.insertRow(_row)
            self.__set_item(_row, 0, _file)
            self.__set_item(_row, 1, 'N/A')
            self.__set_item(_row, 2, 'N/A')
            self.__set_item(_row, 3, 'N/A')
            self.__set_item(_row, 4, 'N/A')

        self.ui.tableWidget.blockSignals(False)

    def __set_item(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if row == self.reference_image_index:
            item.setBackground(self.color_reference_background)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    ## Event Handler

    def calculate_markers_button_clicked(self):
        pass

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def slider_file_changed(self, value):
        pass

    def previous_image_button_clicked(self):
        print("previous")

    def next_image_button_clicked(self):
        pass

    def registered_all_images_button_clicked(self):
        print("registered all images")

    def cancel_button_clicked(self):
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()

    def save_and_close_button_clicked(self):
        """save registered images back to the main UI"""
        self.cancel_button_clicked()

    def opacity_slider_moved(self, value):
        print("opacity slider")

    def closeEvent(self, c):
        print("here")
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()