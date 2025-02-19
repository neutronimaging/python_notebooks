from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
from qtpy import QtGui
import os
import numpy as np
from collections import OrderedDict
import pyqtgraph as pg
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.table_handler import TableHandler
from __code.overlay_images.event_handler import EventHandler


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def dictionaries(self):
        list_high_res_files = self.parent.o_norm_high_res.data['sample']['file_name']
        list_high_res_files_basename = [os.path.basename(_file) for _file in list_high_res_files]
        list_low_res_files = self.parent.o_norm_low_res.data['sample']['file_name']
        list_low_res_files_basename = [os.path.basename(_file) for _file in list_low_res_files]

        dict_offsets = OrderedDict()
        for _index, _filename in enumerate(list_high_res_files_basename):
            dict_offsets[_filename] = {'offset': {'x': 0, 'y': 0},
                                       'low_resolution_filename': list_low_res_files_basename[_index],
                                       }
        self.parent.dict_images_offset = dict_offsets

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def widgets(self):

        # list of files table
        list_high_res_files = self.parent.o_norm_high_res.data['sample']['file_name']
        list_low_res_files = self.parent.o_norm_low_res.data['sample']['file_name']

        list_high_res_files_basename = [os.path.basename(_file) for _file in list_high_res_files]
        list_low_res_files_basename = [os.path.basename(_file) for _file in list_low_res_files]

        resize_and_overlay_modes = []

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        _row = 0
        for _high_res_file, _low_res_file in zip(list_high_res_files_basename, list_low_res_files_basename):
            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row, column=0, value=_high_res_file, editable=False)
            o_table.insert_item(row=_row, column=1, value=_low_res_file, editable=False)
            o_table.insert_item(row=_row, column=2, value="None")
            resize_and_overlay_modes.append("None")
            _row += 1

        o_table.set_column_sizes(column_sizes=[200, 200, 100])
        self.parent.resize_and_overlay_modes = resize_and_overlay_modes

        self.parent.ui.splitter_3.setSizes([400, 400])
        self.parent.ui.splitter_2.setSizes([800, 0])
        self.parent.splitter_state = self.parent.ui.splitter_2.saveState()
        self.parent.ui.splitter_2.setHandleWidth(0)
        self.parent.ui.tabWidget.setTabEnabled(1, False)
        self.parent.splitter_closed_state = self.parent.ui.splitter_2.saveState()

        self.parent.ui.low_resolution_label.setEnabled(False)
        self.parent.ui.high_resolution_label.setEnabled(False)
        self.parent.ui.transparency_slider.setEnabled(False)
        self.parent.ui.transparency_checkBox.setChecked(False)

    def matplotlib(self):

        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=4, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.horizontal_profile_plot = _matplotlib(parent=self.parent,
                                        widget=self.parent.ui.horizontal_profile_widget)
        self.parent.vertical_profile_plot = _matplotlib(parent=self.parent,
                                        widget=self.parent.ui.vertical_profile_widget)

        # self.profile_plot.mpl_connect('button_press_event', self.click_on_profile_plot)


    def pyqtgraph(self):
        
        self.parent.image_view['high_res'] = pg.ImageView(view=pg.PlotItem())
        self.parent.image_view['high_res'].ui.roiBtn.hide()
        self.parent.image_view['high_res'].ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.image_view['high_res'])
        self.parent.ui.high_res_widget.setLayout(image_layout)

        self.parent.image_view['low_res'] = pg.ImageView(view=pg.PlotItem())
        self.parent.image_view['low_res'].ui.roiBtn.hide()
        self.parent.image_view['low_res'].ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.image_view['low_res'])
        self.parent.ui.low_res_widget.setLayout(image_layout)

        self.parent.image_view['overlay'] = pg.ImageView(view=pg.PlotItem())
        self.parent.image_view['overlay'].ui.roiBtn.hide()
        self.parent.image_view['overlay'].ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.image_view['overlay'])
        self.parent.ui.overlay_widget.setLayout(image_layout)

    def _design_marker(self, image_resolution=None,
                       target_index=None,
                       pen=None, image_view=None,
                       method=None):
        x = self.parent.markers[image_resolution][target_index]['x']
        y = self.parent.markers[image_resolution][target_index]['y']
        image_view = self.parent.image_view[image_resolution]

        width = self.parent.markers['width']
        height = self.parent.markers['height']

        ui = pg.ROI([x, y], [width, height], scaleSnap=True, pen=pen)
        image_view.addItem(ui)
        ui.sigRegionChanged.connect(method)
        return ui

    def markers(self):
        red_pen = QtGui.QPen()
        red_pen.setColor(QtGui.QColor(255, 0, 0, 255))
        red_pen.setWidthF(0.05)

        blue_pen = QtGui.QPen()
        blue_pen.setColor(QtGui.QColor(0, 0, 255, 255))
        blue_pen.setWidthF(0.05)

        self.parent.markers['high_res']['1']['ui'] = self._design_marker(image_resolution='high_res',
                                                                         target_index='1',
                                                                         pen=red_pen,
                                                                         method=self.parent.markers_changed)

        self.parent.markers['high_res']['2']['ui'] = self._design_marker(image_resolution='high_res',
                                                                         target_index='2',
                                                                         pen=blue_pen,
                                                                         method=self.parent.markers_changed)

        self.parent.markers['low_res']['1']['ui'] = self._design_marker(image_resolution='low_res',
                                                                        target_index='1',
                                                                        pen=red_pen,
                                                                        method=self.parent.markers_changed)

        self.parent.markers['low_res']['2']['ui'] = self._design_marker(image_resolution='low_res',
                                                                        target_index='2',
                                                                        pen=blue_pen,
                                                                        method=self.parent.markers_changed)

        o_event = EventHandler(parent=self.parent)
        o_event.update_target(image_resolution='high_res', target_index='1')
        o_event.update_target(image_resolution='high_res', target_index='2')
        o_event.update_target(image_resolution='low_res', target_index='1')
        o_event.update_target(image_resolution='low_res', target_index='2')

    def update_profile_markers(self, with_profile=True):
        pass