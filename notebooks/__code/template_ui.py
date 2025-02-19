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

from __code.ui_template  import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def load(self):
        list_images = self.list_images_ui.selected
        o_norm = Normalization()
        o_norm.load(file=list_images, notebook=True)
        self.o_norm = o_norm


class Interface(QMainWindow):

    live_data = []

    def __init__(self, parent=None, o_norm=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        self.o_norm = o_norm

        self.list_files = self.o_norm.data['sample']['file_name']
        self.list_data = self.o_norm.data['sample']['data']

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Template UI")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        bottom_layout = QtGui.QHBoxLayout()

        # file index slider
        label_1 = QtGui.QLabel("File Index")
        self.ui.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.ui.slider.setMaximum(len(self.list_files) - 1)
        self.ui.slider.setMinimum(0)
        self.ui.slider.valueChanged.connect(self.file_index_changed)

        # spacer
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        bottom_layout.addWidget(label_1)
        bottom_layout.addWidget(self.ui.slider)
        bottom_layout.addItem(spacer)

        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(bottom_layout)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        vertical_layout.addWidget(bottom_widget)

        self.ui.widget.setLayout(vertical_layout)

        self.init_widgets()
        self.file_index_changed()

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



