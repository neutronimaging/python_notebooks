#from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import HTML
from IPython.display import display
import ipywe.fileselector

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import numpy as np
import os

import pyqtgraph as pg

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication

from __code import file_handler
from __code.ui_linear_profile import Ui_MainWindow as UiMainWindow

