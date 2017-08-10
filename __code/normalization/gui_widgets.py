try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
import os
from __code.deal_images.decorators import format_directory
import platform


@format_directory
def gui_dname(dir=None, message=''):
    """Select files"""
    if message == '':
        message = 'Select Folder ...'
    dirname = QFileDialog.getExistingDirectory(None, message, 
                                            dir, 
                                            QFileDialog.ShowDirsOnly)

    if platform.system() == 'Linux':
        return dirname
    else:
        return dirname

@format_directory
def gui_fname(dir=None, message='', ext='tif'):
    """Select one or more file via a dialog and returns the file name.
    """
    _filter = ''
    if ext == 'tif':
        _filter = "TIFF (*.tif)"
    elif ext == 'fits':
        _filter = "FITS (*.fits)"
    elif ext == 'txt':
        _filter = "ascii (*.txt)"
    elif ext == 'dat':
        _filter = "data (*.dat)"
    elif ext == 'csv':
        _filter = 'ascii (*.csv)'
    else:
        _filter = '{} (*{})'.format(ext, ext)
    _filter = _filter + ";;All (*.*)"
        
    fname = QFileDialog.getOpenFileNames(None, message,
                                         directory = dir, 
                                         filter = _filter)

    if isinstance(fname, tuple):
        return fname[0]
    return fname

@format_directory
def gui_fimage(dir=None, message=''):
    """Select one or more image via a dialog and returns the file name.
    """
    _filter = 'FITS (*.fits);; TIFF (*.tiff);; TIFF (*.tif)'
    fname = QFileDialog.getOpenFileNames(None, message,
                                         directory = dir, 
                                         filter = _filter)

    return fname
    
@format_directory
def gui_single_file(dir=None):
    """Select one o file via a dialog and returns the file name.
    """
    if dir is None: 
        dir ='./'
    fname = QFileDialog.getOpenFileName(None, "Select file...", 
            dir, filter="Spectra File (*_Spectra.txt)")
    return fname


@format_directory
def gui_csv_fname(dir=None):
    """Select one or more file via a dialog and returns the file name.
    """
    if dir is None: 
        dir ='./'
    fname = QFileDialog.getOpenFileNames(None, "Select file(s)...", 
            dir, filter="Fits files(*.csv)")
    return fname
