import os
import pyqtgraph as pg
from qtpy import QtCore
from qtpy import QtGui
from qtpy.QtWidgets import QApplication
from IPython.core.display import HTML
from IPython.core.display import display
import collections
from PIL import Image
import numpy as np
from skimage import transform
import pandas as pd

from __code.metadata_overlapping_images.metadata_string_format_handler import MetadataStringFormatLauncher
from __code.file_handler import retrieve_time_stamp
from __code.metadata_overlapping_images.general_classes import ScaleSettings, MetadataSettings


class ExportImages:

    ext = '.png'

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def _create_output_file_name(self, file=''):
        if file == '':
            return ''

        basename_ext = os.path.basename(file)
        [basename, ext] = os.path.splitext(basename_ext)

        full_file_name = os.path.join(self.export_folder, basename + self.ext)
        return full_file_name

    def run(self):

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.parent.eventProgress.setMinimum(1)
        self.parent.eventProgress.setMaximum(len(self.parent.data_dict['file_name']))
        self.parent.eventProgress.setValue(1)
        self.parent.eventProgress.setVisible(True)

        for _index, _file in enumerate(self.parent.data_dict['file_name']):
            output_file_name = self._create_output_file_name(file=_file)
            self.parent.ui.file_slider.setValue(_index)

            exporter = pg.exporters.ImageExporter(self.parent.ui.image_view.view)

            exporter.params.param('width').setValue(2024, blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(2014, blockSignal=exporter.heightChanged)

            exporter.export(output_file_name)

            self.parent.eventProgress.setValue(_index+2)
            QtGui.QGuiApplication.processEvents()

        QtGui.QGuiApplication.processEvents()

        display(HTML("Exported Images in Folder {}".format(self.export_folder)))
        self.parent.eventProgress.setVisible(False)
        QApplication.restoreOverrideCursor()


class Initializer:

    def __init__(self, parent=None):
        self.parent = parent

    def timestamp_dict(self):
        list_files = self.parent.data_dict['file_name']
        self.parent.timestamp_dict = retrieve_time_stamp(list_files)

    def parameters(self):
        self.parent.scale_settings = ScaleSettings()
        self.parent.metadata_settings  = MetadataSettings()

    def statusbar(self):
        self.parent.eventProgress = QtGui.QProgressBar(self.parent.ui.statusbar)
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
            self.set_item_table(row=_row, col=0, value=_file)
            self.set_item_table(row=_row, col=1, value="N/A", editable=True)
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
        list_metadata = self.get_list_metadata()
        if list_metadata:
            self.parent.ui.select_metadata_combobox.addItems(list_metadata)
        else: #hide widgets
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
        self.parent.ui.scale_size_spinbox.setValue(np.int(max_value/4))

        # metadata and scale slider positions
        self.parent.ui.scale_position_x.setMaximum(width)
        self.parent.ui.scale_position_y.setMaximum(height)

        self.parent.ui.metadata_position_x.setMinimum(0)
        self.parent.ui.metadata_position_x.setMaximum(width)
        self.parent.ui.metadata_position_y.setMaximum(height)
        self.parent.ui.metadata_position_y.setValue(height)

        self.parent.ui.graph_position_x.setMinimum(0)
        self.parent.ui.graph_position_x.setMaximum(width)
        self.parent.ui.graph_position_x.setValue(np.int(width/2))
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
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def set_item_all_plot_file_name_table(self, row=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.all_plots_file_name_table.setItem(row, 0, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_table(self, row=0, col=0, value='', editable=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.tableWidget.setItem(row, col, item)
        if not editable:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def get_list_metadata(self):
        first_file = self.parent.data_dict['file_name'][0]
        [_, ext] = os.path.splitext(os.path.basename(first_file))
        if ext in [".tif", ".tiff"]:
            o_image0 = Image.open(first_file)
            info = collections.OrderedDict(sorted(o_image0.tag_v2.items()))
            list_metadata = []
            list_key = []
            for tag, value in info.items():
                list_metadata.append("{} -> {}".format(tag, value))
                list_key.append(tag)
            self.parent.list_metadata = list_key
            return list_metadata
        else:
            return []


class DisplayImages:

    def __init__(self, parent=None, recalculate_image=False):
        self.parent = parent
        self.recalculate_image = recalculate_image

        self.display_images()
        # self.display_grid()

    def get_image_selected(self, recalculate_image=False):
        slider_index = self.parent.ui.file_slider.value()
        if recalculate_image:
            angle = self.parent.rotation_angle
            # rotate all images
            self.parent.data_dict['data'] = [transform.rotate(_image, angle) for _image in self.parent.data_dict_raw['data']]

        _image = self.parent.data_dict['data'][slider_index]
        return _image

    def display_images(self):
        _image = self.get_image_selected(recalculate_image=self.recalculate_image)
        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0], self.parent.histogram_level[1])


class TableLoader:

    table = {}

    def __init__(self, parent=None, filename=''):
        self.parent = parent
        self.filename = filename

    def load_table(self):
        table = pd.read_csv(self.filename,
                            sep=',',
                            comment='#',
                            names=["filename", "metadata"])
        table_dict = {}
        for _row in table.values:
            _key, _value = _row
            table_dict[_key] = _value

        self.table = table_dict

    def populate(self):
        """This will look at the filename value in the first column of tableWidget and if they match if any
        of the key of the dictionary, it will populate the value column"""

        # populate with new entries
        nbr_row = self.parent.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            table_key = self.parent.ui.tableWidget.item(_row, 0).text()
            value = self.table.get(table_key, "")
            self.parent.ui.tableWidget.item(_row, 1).setText(str(value))


class MetadataTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self, position=None):
        menu = QtGui.QMenu(self.parent)

        _format = menu.addAction("Clean String ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _format:
            self.format_metadata_column()

    def format_metadata_column(self):
        MetadataStringFormatLauncher(parent=self.parent)
