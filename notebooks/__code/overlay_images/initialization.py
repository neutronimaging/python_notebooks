from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
import os
from collections import OrderedDict
import pyqtgraph as pg

from __code._utilities.table_handler import TableHandler


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def dictionaries(self):
        list_high_reso_files = self.parent.o_norm_high_reso.data['sample']['file_name']
        list_high_reso_files_basename = [os.path.basename(_file) for _file in list_high_reso_files]
        list_low_reso_files = self.parent.o_norm_low_reso.data['sample']['file_name']
        list_low_reso_files_basename = [os.path.basename(_file) for _file in list_low_reso_files]

        dict_offsets = OrderedDict()
        for _index, _filename in enumerate(list_high_reso_files_basename):
            dict_offsets[_filename] = {'offset': {'x': 0, 'y': 0},
                                       'low_resolution_filename': list_low_reso_files_basename[_index],
                                       }
        self.parent.dict_images_offset = dict_offsets

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def widgets(self):
        # list of files table
        list_high_reso_files = self.parent.o_norm_high_reso.data['sample']['file_name']
        list_low_reso_files = self.parent.o_norm_low_reso.data['sample']['file_name']

        list_high_reso_files_basename = [os.path.basename(_file) for _file in list_high_reso_files]
        list_low_reso_files_basename = [os.path.basename(_file) for _file in list_low_reso_files]

        dict_images_offset = self.parent.dict_images_offset

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        _row = 0
        for _high_reso_file, _low_reso_file in zip(list_high_reso_files_basename, list_low_reso_files_basename):
            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row, column=0, value=_high_reso_file, editable=False)
            o_table.insert_item(row=_row, column=1, value=_low_reso_file, editable=False)
            o_table.insert_item(row=_row, column=2, value=dict_images_offset[_high_reso_file]['offset']['x'])
            o_table.insert_item(row=_row, column=3, value=dict_images_offset[_high_reso_file]['offset']['y'])
            _row += 1

        o_table.set_column_sizes(column_sizes=[200, 200, 50, 50])

        self.parent.ui.splitter_2.setSizes([200, 500])

    def pyqtgraph(self):
        self.parent.ui.high_resolution_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.high_resolution_image_view.ui.roiBtn.hide()
        self.parent.ui.high_resolution_image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.high_resolution_image_view)
        self.parent.ui.high_res_widget.setLayout(image_layout)

        self.parent.ui.low_resolution_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.low_resolution_image_view.ui.roiBtn.hide()
        self.parent.ui.low_resolution_image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.low_resolution_image_view)
        self.parent.ui.low_res_widget.setLayout(image_layout)
