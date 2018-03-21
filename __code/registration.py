import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets

import numpy as np
import os
import re
import glob
from scipy.special import erf
from scipy.optimize import curve_fit
import pprint

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from __code.file_handler import make_ascii_file

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization


from __code.ui_registration  import Ui_MainWindow as UiMainWindow


class RegistrationUi(QMainWindow):


    def __init__(self, parent=None, data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration")

        self.data_dict = data_dict # Normalization data dictionary

    # Event handler
    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def ok_button_clicked(self):
        # do soemthing here
        self.close()

    def cancel_button_clicked(self):
        self.close()


class RegistrationFileSelection(object):

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def load_files(self, files):
        o_norm = Normalization()
        o_norm.load(file=files, notebook=True)
        self.data_dict = o_norm.data

    def select_data(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                             start_dir=self.working_dir,
                                                             next=self.load_files,
                                                             multiple=True)

        self.files_ui.show()
