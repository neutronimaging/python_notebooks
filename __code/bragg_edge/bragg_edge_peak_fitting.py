from IPython.core.display import HTML
import os
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
from __code import load_ui


class BraggEdge(BraggEdgeParent):

   pass



class Interface(QMainWindow):

    histogram_level = []

    def __init__(self, parent=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_bragg_edge_peak_fitting.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Peak Fitting Tool")

        # initialization
        o_init = Initialization(parent=self)
        o_init.init_statusbar()
        o_init.init_pyqtgraph()
        o_init.init_widgets()

    # event handler
    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
