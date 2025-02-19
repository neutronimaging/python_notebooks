import os
import numpy as np
from qtpy.QtWidgets import QTableWidgetItem, QVBoxLayout
import pyqtgraph as pg
from qtpy import QtCore

from __code import interact_me_style
from __code.file_handler import retrieve_time_stamp


class Initializer:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.timestamp_dict()
        self.table()
        self.parameters()
        self.widgets()
        self.pyqtgraph()

    def timestamp_dict(self):
        list_files = self.parent.data_dict['file_name']
        self.parent.timestamp_dict = retrieve_time_stamp(list_files)

    def table(self):
        # init the summary table
        list_files_full_name = self.parent.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        list_time_stamp = self.parent.timestamp_dict['list_time_stamp']
        list_time_stamp_user_format = self.parent.timestamp_dict['list_time_stamp_user_format']
        time_0 = list_time_stamp[0]
        for _row, _file in enumerate(list_files_short_name):
            self.parent.ui.summary_table.insertRow(_row)
            self.set_item_summary_table(row=_row, col=0, value=_file)
            self.set_item_summary_table(row=_row, col=1, value=list_time_stamp_user_format[_row])
            _offset = list_time_stamp[_row] - time_0
            self.set_item_summary_table(row=_row, col=2, value="{:0.2f}".format(_offset))

            self.parent.ui.all_plots_file_name_table.insertRow(_row)
            self.set_item_all_plot_file_name_table(row=_row, value=os.path.basename(_file))

    def parameters(self):
        # init the position of the measurement ROI
        [height, width] = np.shape(self.parent.data_dict['data'][0])
        self.parent.default_guide_roi['width'] = int(width / 10)
        self.parent.default_guide_roi['height'] = int(height / 5)
        self.parent.default_guide_roi['x0'] = int(width / 2)
        self.parent.default_guide_roi['y0'] = int(height / 2)
        self.parent.default_profile_width_values = [str(_value) for _value in self.parent.default_profile_width_values]

    def widgets(self):
        _file_path = os.path.dirname(__file__)
        left_rotation_fast_file = os.path.abspath(os.path.join(_file_path,
                                                               '../static/profile/button_rotation_left_fast.png'))
        self.parent.ui.left_rotation_button_fast.setStyleSheet("background-image: "
                                                               "url('" + left_rotation_fast_file + "'); " + \
                                                               "background-repeat: no-repeat")

        right_rotation_fast_file = os.path.abspath(os.path.join(_file_path,
                                                                '../static/profile/button_rotation_right_fast.png'))
        self.parent.ui.right_rotation_button_fast.setStyleSheet("background-image: "
                                                                "url('" + right_rotation_fast_file + "'); " + \
                                                                "background-repeat: no-repeat")

        left_rotation_slow_file = os.path.abspath(os.path.join(_file_path,
                                                               '../static/profile/button_rotation_left_slow.png'))
        self.parent.ui.left_rotation_button_slow.setStyleSheet("background-image: "
                                                               "url('" + left_rotation_slow_file + "'); " + \
                                                               "background-repeat: no-repeat")

        right_rotation_slow_file = os.path.abspath(os.path.join(_file_path,
                                                                '../static/profile/button_rotation_right_slow.png'))
        self.parent.ui.right_rotation_button_slow.setStyleSheet("background-image: "
                                                                "url('" + right_rotation_slow_file + "'); " + \
                                                                "background-repeat: no-repeat")

        self.parent.ui.splitter_2.setSizes([250, 50])
        self.parent.ui.splitter.setSizes([500, 50])
        self.parent.ui.all_plots_hori_splitter.setSizes([250, 100])
        self.parent.ui.all_plots_verti_splitter.setSizes([300, 100])

        # file slider
        self.parent.ui.file_slider.setMaximum(len(self.parent.data_dict['data']) - 1)

        # update size of table columns
        nbr_columns = self.parent.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.tableWidget.setColumnWidth(_col, self.parent.guide_table_width[_col])

        # update size of summary table
        nbr_columns = self.parent.ui.summary_table.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.summary_table.setColumnWidth(_col, self.parent.summary_table_width[_col])

        self.parent.display_ui = [self.parent.ui.display_size_label,
                                  self.parent.ui.grid_size_slider,
                                  self.parent.ui.display_transparency_label,
                                  self.parent.ui.transparency_slider]

        self.parent.ui.pushButton_5.setStyleSheet(interact_me_style)

    def pyqtgraph(self):
        # image
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

        # profile
        self.parent.ui.profile_view = pg.PlotWidget()
        self.parent.ui.profile_view.plot()
        self.parent.legend = self.parent.ui.profile_view.addLegend()
        vertical_layout2 = QVBoxLayout()
        vertical_layout2.addWidget(self.parent.ui.profile_view)
        self.parent.ui.profile_widget.setLayout(vertical_layout2)

        # all plots
        self.parent.ui.all_plots_view = pg.PlotWidget()
        self.parent.ui.all_plots_view.plot()
        self.parent.all_plots_legend = self.parent.ui.all_plots_view.addLegend()
        vertical_layout2 = QVBoxLayout()
        vertical_layout2.addWidget(self.parent.ui.all_plots_view)
        self.parent.ui.all_plots_widget.setLayout(vertical_layout2)

    def set_item_all_plot_file_name_table(self, row=0, value=''):
        item = QTableWidgetItem(str(value))
        self.parent.ui.all_plots_file_name_table.setItem(row, 0, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_summary_table(self, row=0, col=0, value=''):
        item = QTableWidgetItem(str(value))
        self.parent.ui.summary_table.setItem(row, col, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
