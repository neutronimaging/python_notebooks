# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + run_control={"frozen": false, "read_only": false}
from PyQt5 import QtGui, QtCore

# + run_control={"frozen": false, "read_only": false}
# -*- coding: utf-8 -*-
"""
This example demonstrates the use of ImageView, which is a high-level widget for 
displaying and analyzing 2D and 3D data. ImageView provides:

  1. A zoomable region (ViewBox) for displaying the image
  2. A combination histogram and gradient editor (HistogramLUTItem) for
     controlling the visual appearance of the image
  3. A timeline for selecting the currently displayed frame (for 3D data only).
  4. Tools for very basic analysis of image data (see ROI and Norm buttons)

"""
## Add path to library (just for examples; you do not need this)
#import initExample

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()

def refresh():
    global imv, init_state
    _item = imv.getImageItem()
    _view = imv.getView()
    _state = _view.getState()
    _view.setState(init_state)
    print("viewRange: {}".format(_state['viewRange']))
    print("targetRange: {}".format(_state['targetRange']))
    print()

save_state = dict()
    
def restore_state():
    global imv, save_state
    _item = imv.getImageItem()
    _view = imv.getView()
    print("restoring state: {}".format(save_state))
    _view.setState(save_state)
    
def save_state():
    global imv, save_state
    _item = imv.getImageItem()
    _view = imv.getView()
    _save_state = _view.getState(copy=False)
    import copy
    save_state = copy.deepcopy(_save_state)
    print("saved state: {}".format(save_state))
    
    # reset state
    #_view.setState(init_state)
    
# _roi = pg.ROI([0,0,200,200])
# _roi.addScaleHandle([1,1],[0,0])
# _roi.sigRegionChanged.connect(refresh)
# imv.addItem(_roi)

main_widget = QtGui.QWidget()
_button = QtGui.QPushButton("push me")
vertical_layout = QtGui.QVBoxLayout()
vertical_layout.addWidget(imv)
vertical_layout.addWidget(_button)

_save_button = QtGui.QPushButton("save")
vertical_layout.addWidget(_save_button)

_set_state_button = QtGui.QPushButton("apply save state")
vertical_layout.addWidget(_set_state_button)

_button.clicked.connect(refresh)
_save_button.clicked.connect(save_state)        
_set_state_button.clicked.connect(restore_state)

main_widget.setLayout(vertical_layout)

#win.setCentralWidget(imv)
win.setCentralWidget(main_widget)
win.show()
win.setWindowTitle('pyqtgraph example: ImageView')

## Create random 3D data set with noisy signals
img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100
img = img[np.newaxis,:,:]
decay = np.exp(-np.linspace(0,0.3,100))[:,np.newaxis,np.newaxis]
data = np.random.normal(size=(100, 200, 200))
data += img * decay
data += 2

## Add time-varying signal
sig = np.zeros(data.shape[0])
sig[30:] += np.exp(-np.linspace(1,10, 70))
sig[40:] += np.exp(-np.linspace(1,10, 60))
sig[70:] += np.exp(-np.linspace(1,10, 30))

sig = sig[:,np.newaxis,np.newaxis] * 3
data[:,50:60,30:40] += sig

## Display the data and assign each frame a time value from 1.0 to 3.0
imv.setImage(data, xvals=np.linspace(1., 3., data.shape[0]))

## Set a custom color map
colors = [
    (0, 0, 0),
    (45, 5, 61),
    (84, 42, 55),
    (150, 87, 60),
    (208, 171, 141),
    (255, 255, 255)
]
cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
imv.setColorMap(cmap)

_item = imv.getImageItem()
_view = imv.getView()

# save initial state
init_state = _view.getState()

#padding
x0=0; x1=-7; y0=200; y1=200
width = x1-x0
height = y1-y0
_view.setRange(rect=QtCore.QRectF(x0, y0, width, height))

#zoom
zoom_x0 = -25
zoom_x1 = 29
zoom_y0 = 167
zoom_y1 = 225

init_state = _view.getState()


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


# + run_control={"frozen": false, "read_only": false}
imv.getView().setState(save_state)

# + run_control={"frozen": false, "read_only": false}
_item = imv.getImageItem()
_view = imv.getView()

# + run_control={"frozen": false, "read_only": false}
print(_view.itemBoundingRect(_item))

# + run_control={"frozen": false, "read_only": false}
view_widget = _view.getViewWidget()

# + run_control={"frozen": false, "read_only": false}
my_view.screenGeometry()

# + run_control={"frozen": false, "read_only": false}
_item = imv.getImageItem()
_view = imv.getView()
_view.setRange(xRange=(-7.68, 207))
