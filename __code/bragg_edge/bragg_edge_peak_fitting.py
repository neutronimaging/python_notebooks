from IPython.core.display import HTML
from IPython.display import display
try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code.ui_bragg_edge_peak_fitting import Ui_MainWindow as UiMainWindow

class BraggEdge(BraggEdgeParent):

   pass



class Interface(QMainWindow):

    histogram_level = []

    def __init__(self, parent=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Peak Fitting Tool")

        # initialization
        o_init = Initialization(parent=self)
        o_init.init_statusbar()
        o_init.init_pyqtgraph()

    # event handler
    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
