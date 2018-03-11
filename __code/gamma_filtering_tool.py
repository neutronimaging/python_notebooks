from IPython.core.display import HTML
from IPython.display import display

import pyqtgraph as pg

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.ui_gamma_filtering_tool  import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def get_list_of_files(self):
        return self.list_images_ui.selected


class Interface(QMainWindow):

    live_data = []

    def __init__(self, parent=None, list_of_files=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.list_files = self.list_of_files

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        # self.init_statusbar()

        self.init_pyqtgraph()
        self.init_widgets()

    def init_pyqtgraph(self):

        self.ui.raw_image_view = pg.ImageView()
        self.ui.raw_image_view.ui.roiBtn.hide()
        self.ui.raw_image_view.ui.menuBtn.hide()
        left_layout = QtGui.QHBoxLayout()
        left_layout.addWiget(self.ui.raw_image_view)
        self.ui.left_widget.setLayout(left_layout)

        self.ui.filtered_image_view = pg.ImageView()
        self.ui.filtered_image_view.ui.roiBtn.hide()
        self.ui.filtered_image_view.ui.menuBtn.hide()
        center_layout = QtGui.QHBoxLayout()
        center_layout.addWidget(self.ui.filtered_image_view)
        self.ui.left_widget.setLayout(center_layout)

        self.ui.diff_image_view = pg.ImageView()
        self.ui.diff_image_view.ui.roiBtn.hide()
        self.ui.diff_image_view.ui.menuBtn.hide()
        right_layout = QtGui.QHBoxLayout()
        right_layout.addWidget(self.ui.diff_image_view)
        self.ui.left_widget.setLayout(right_layout)

    def init_widgets(self):
        pass

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        file_index = self.ui.slider.value()
        new_live_image = self.list_data[file_index]
        self.ui.image_view.setImage(new_live_image)
        self.ui.file_name.setText(self.list_files[file_index])

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



