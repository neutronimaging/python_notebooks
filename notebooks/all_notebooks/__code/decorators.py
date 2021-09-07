import os

try:
    from PyQt4.QtGui import QApplication
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5 import QtCore, QtGui


def format_directory(function):
    '''
    This decorator will make sure the directory format is correct for the right
    os system. On Mac, pyqt does not like seing the '\' replacing the white spaces.
    '''
    
    def new_function(dir=None, **kwargs):

        if dir is None:
            dir = './'
        elif dir == "":
            dir = './'
        else:
            if os.sys.platform == 'darwin':
                dir = dir.replace('\\','')
        return function(dir=dir, **kwargs)
                
    return new_function


def wait_cursor(function):
    """
    Add a wait cursor during the running of the function
    """
    def wrapper(*args, **kwargs):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        QtGui.QGuiApplication.processEvents()
        function(*args, **kwargs)
        # function(self)
        QApplication.restoreOverrideCursor()
        QtGui.QGuiApplication.processEvents()

    return wrapper
