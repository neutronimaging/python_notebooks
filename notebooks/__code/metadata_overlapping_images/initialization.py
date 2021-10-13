import os
import pyqtgraph as pg
from qtpy import QtCore
from qtpy.QtWidgets import QVBoxLayout, QProgressBar, QTableWidgetItem
import numpy as np

from __code.file_handler import retrieve_time_stamp
from __code.metadata_overlapping_images.general_classes import ScaleSettings, MetadataSettings
from .get import Get


class Initializer:

    def __init__(self, parent=None):
        self.parent = parent

    def timestamp_dict(self):
        list_files = self.parent.data_dict['file_name']
        self.parent.timestamp_dict = retrieve_time_stamp(list_files)

    def parameters(self):
        self.parent.scale_settings = ScaleSettings()
        self.parent.metadata_settings = MetadataSettings()

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(300, 20)
        self.parent.eventProgress.setMaximumSize(300, 20)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def table(self):
        # init the summary table
        list_files_full_name = self.parent.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        self.parent.ui.tableWidget.blockSignals(True)
        for _row, _file in enumerate(list_files_short_name):
            self.parent.ui.tableWidget.insertRow(_row)
            self.set_item_table(row=_row, col=0, value=_row)
            self.set_item_table(row=_row, col=1, value=_file)
            self.set_item_table(row=_row, col=2, value="N/A", editable=True)
            self.set_item_table(row=_row, col=3, value="N/A", editable=True)
        self.parent.ui.tableWidget.blockSignals(False)

    def set_scale_spinbox_max_value(self):
        [height, width] = np.shape(self.parent.data_dict['data'][0])
        if self.parent.ui.scale_horizontal_orientation.isChecked():
            max_value = width
        else:
            max_value = height
        self.parent.ui.scale_size_spinbox.setMaximum(max_value)

    def widgets(self):

        # splitter
        self.parent.ui.splitter.setSizes([800, 50])

        # file slider
        self.parent.ui.file_slider.setMaximum(len(self.parent.data_dict['data']) - 1)

        # update size of table columns
        nbr_columns = self.parent.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.tableWidget.setColumnWidth(_col, self.parent.guide_table_width[_col])

        # populate list of metadata if file is a tiff
        o_get = Get(parent=self.parent)
        list_metadata = o_get.list_metadata()
        self.parent.raw_list_metadata = list_metadata
        if list_metadata:
            self.parent.ui.select_metadata_combobox.addItems(list_metadata)
        else: # hide widgets
            self.parent.ui.select_metadata_checkbox.setVisible(False)
            self.parent.ui.select_metadata_combobox.setVisible(False)

        # list of scale available
        self.parent.ui.scale_units_combobox.addItems(self.parent.list_scale_units['string'])

        # pixel size range
        [height, width] = np.shape(self.parent.data_dict['data'][0])
        self.set_scale_spinbox_max_value()
        if self.parent.ui.scale_horizontal_orientation.isChecked():
            max_value = width
        else:
            max_value = height
        self.parent.ui.scale_size_spinbox.setValue(int(max_value/4))

        # metadata and scale slider positions
        self.parent.ui.scale_position_x.setMaximum(width)
        self.parent.ui.scale_position_y.setMaximum(height)

        self.parent.ui.metadata_position_x.setMinimum(0)
        self.parent.ui.metadata_position_x.setMaximum(width)
        self.parent.ui.metadata_position_y.setMaximum(height)
        self.parent.ui.metadata_position_y.setValue(height)

        self.parent.ui.graph_position_x.setMinimum(0)
        self.parent.ui.graph_position_x.setMaximum(width)
        self.parent.ui.graph_position_x.setValue(int(width/2))
        self.parent.ui.graph_position_y.setMaximum(height)
        self.parent.ui.graph_position_y.setValue(height)

        # disable the graph sliders groupBox
        self.parent.ui.graph_groupBox.setEnabled(False)

    def event(self):
        # table event
        self.parent.ui.tableWidget.cellChanged.connect(self.parent.table_cell_changed)

    def pyqtgraph(self):
        # image
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def set_item_all_plot_file_name_table(self, row=0, value=''):
        item = QTableWidgetItem(str(value))
        self.parent.ui.all_plots_file_name_table.setItem(row, 1, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_table(self, row=0, col=0, value='', editable=False):
        item = QTableWidgetItem(str(value))
        self.parent.ui.tableWidget.setItem(row, col, item)
        if not editable:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    # def get_list_metadata(self):
    #     first_file = self.parent.data_dict['file_name'][0]
    #     [_, ext] = os.path.splitext(os.path.basename(first_file))
    #     if ext in [".tif", ".tiff"]:
    #         o_image0 = Image.open(first_file)
    #         info = collections.OrderedDict(sorted(o_image0.tag_v2.items()))
    #         list_metadata = []
    #         list_key = []
    #         for tag, value in info.items():
    #             list_metadata.append("{} -> {}".format(tag, value))
    #             list_key.append(tag)
    #         self.parent.list_metadata = list_key
    #         return list_metadata
    #     else:
    #         return []
