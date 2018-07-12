from IPython.core.display import HTML
from IPython.core.display import display

import numpy as np
import os
import copy
import collections
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
from skimage import transform
from PIL import Image

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow, QDialog
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


from __code.file_handler import retrieve_time_stamp
from __code.ui_metadata_overlapping_images import Ui_MainWindow as UiMainWindow


class ScaleSettings:

    x0 = 50
    y0 = 50
    thickness = 10

    cursor_width = 10
    cursor_height = 10

    color = [255, 255, 255]  # white


class MetadataSettings:

    x0 = 200
    y0 = 200

    color = [255, 255, 255] # white


class MetadataOverlappingImagesUi(QMainWindow):

    data_dict = {}
    data_dict_raw = {}
    timestamp_dict = {}
    default_scale_roi = None

    rotation_angle = 0
    histogram_level = []

    # scale pyqtgraph
    scale_pyqt_ui = None
    scale_legend_pyqt_ui = None
    metadata_pyqt_ui = None

    # size of tables
    guide_table_width = [300, 50]

    live_image = []
    display_ui = []

    # guide and profile pg ROIs
    list_guide_pyqt_roi = list()
    list_profile_pyqt_roi = list()
    list_table_widget_checkbox = list()

    list_metadata = []
    list_scale_units = ["mm", u"\u00B5m", "nm"]
    list_scale_units = {'string': ["mm", u"\u00B5m", "nm"],
                        'html': ["mm", "<span>&#181;m</span>", "nm"]}

    rgb_color = {'white': (255, 255, 255, 255, None),
                   'red': (255, 0, 0, 255, None),
                   'green': (0, 255, 0, 255, None),
                   'blue': (0, 0, 255, 255, None),
                   'black': (0, 0, 0, 255, None)}

    html_color = {'white': "#FFF",
                  'red': "#F00",
                  'green': "#0F0",
                  'blue': "#00F",
                  'black': "#000"}


    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Metadata Overlapping Images")

        self.working_dir = working_dir
        self.data_dict = data_dict # Normalization data dictionary  {'file_name': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        o_initialization = Initializer(parent=self)
        o_initialization.parameters()
        o_initialization.statusbar()
        o_initialization.table()
        o_initialization.widgets()
        o_initialization.pyqtgraph()

        # display first images
        self.slider_file_changed(0)

    # ========================================================================================
    # MAIN UI EVENTs

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)
        self.update_metadata_pyqt_ui()

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)
        self.update_metadata_pyqt_ui()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/metadata_overlapping_images/")

    def closeEvent(self, event=None):
        pass

    def slider_file_changed(self, slider_value):
        self.display_image()
        self.ui.image_slider_value.setText(str(slider_value))
        self.check_status_next_prev_image_button()
        self.update_metadata_pyqt_ui()

    def slider_file_clicked(self):
        current_slider_value = self.ui.file_slider.value()
        self.slider_file_changed(current_slider_value)
        self.update_metadata_pyqt_ui()

    def scale_checkbox_clicked(self, status):
        self.ui.scale_groupbox.setEnabled(status)
        self.ui.scale_position_label.setEnabled(status)
        self.ui.scale_position_frame.setEnabled(status)
        self.display_scale_pyqt_ui()

    def metadata_checkbox_clicked(self, status):
        self.ui.metadata_groupbox.setEnabled(status)
        self.ui.metadata_position_label.setEnabled(status)
        self.ui.metadata_position_frame.setEnabled(status)
        self.ui.meta_label.setEnabled(status)
        self.ui.manual_metadata_name.setEnabled(status)
        self.display_metadata_pyqt_ui()

    def select_metadata_checkbox_clicked(self, status):
        self.ui.select_metadata_combobox.setEnabled(status)
        self.update_metadata_pyqt_ui()

    def metadata_list_changed(self, index):
        key_selected = self.list_metadata[index]

        for row, _file in enumerate(self.data_dict['file_name']):
            o_image = Image.open(_file)
            o_dict = dict(o_image.tag_v2)
            value = o_dict[float(key_selected)]
            self.ui.tableWidget.item(row, 1).setText("{}".format(value))

        self.update_metadata_pyqt_ui()

    def scale_orientation_clicked(self):
        o_init = Initializer(parent=self)
        o_init.set_scale_spinbox_max_value()
        self.update_scale_pyqt_ui()

    def scale_thickness_value_changed(self, value):
        self.update_scale_pyqt_ui()

    def scale_color_changed(self, value):
        self.update_scale_pyqt_ui()

    def scale_size_changed(self, value):
        self.update_scale_pyqt_ui()

    def scale_real_size_changed(self):
        """update the label of the scale"""
        self.update_scale_pyqt_ui()

    def scale_units_changed(self):
        self.update_scale_pyqt_ui()

    def scale_position_moved(self, new_value):
        self.update_scale_pyqt_ui()

    def scale_position_clicked(self):
        self.update_scale_pyqt_ui()

    def metadata_position_moved(self, new_value):
        self.update_metadata_pyqt_ui()

    def metadata_position_clicked(self):
        self.update_metadata_pyqt_ui()

    def metadata_color_changed(self, value):
        self.update_metadata_pyqt_ui()

    def metadata_name_return_pressed(self):
        self.update_metadata_pyqt_ui()

    def metadata_text_or_graph_clicked(self):
        status = self.ui.metadata_graph_option.isChecked()
        self.ui.metadata_graph_size_label.setVisible(status)
        self.ui.metadata_graph_size_slider.setVisible(status)
        self.update_metadata_pyqt_ui()

    def metadata_graph_size_pressed(self):
        self.update_metadata_pyqt_ui()

    def metadata_graph_size_moved(self, slider_value):
        self.update_metadata_pyqt_ui()

    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=os.path.dirname(self.working_dir),
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        QtGui.QGuiApplication.processEvents()
        if _export_folder:
            o_export = ExportImages(parent=self,
                                    export_folder=_export_folder)
            o_export.run()

    def import_table_pressed(self):
        _table_file = QFileDialog.getOpenFileName(self,
                                                  directory=os.path.dirname(self.working_dir),
                                                  caption="Select Input File")
        QtGui.QGuiApplication.processEvents()

        if type(_table_file) is tuple:
            _table_file = _table_file[0]

        if _table_file:
            o_import = TableLoader(parent=self,
                                   filename=str(_table_file))
            o_import.load_table()
            o_import.populate()
            self.update_metadata_pyqt_ui()

    # ========================================================================================

    def update_metadata_pyqt_ui(self):
        if self.metadata_pyqt_ui:
            self.ui.image_view.removeItem(self.metadata_pyqt_ui)
        try:
            if self.ui.image_view:
                pass
        except:
            return
        self.display_metadata_pyqt_ui()

    def update_scale_pyqt_ui(self):
        if self.scale_pyqt_ui:
            self.ui.image_view.removeItem(self.scale_pyqt_ui)
        if self.scale_legend_pyqt_ui:
            self.ui.image_view.removeItem(self.scale_legend_pyqt_ui)
        try:
            if self.ui.image_view:
                pass
        except:
            return
        self.display_scale_pyqt_ui(view=self.ui.image_view)

    def get_color(self, color_type='html', source='metadata'):
        if source == 'metadata':
            color_selected = self.ui.metadata_color_combobox.currentText().lower()
        else:
            color_selected = self.ui.scale_color_combobox.currentText().lower()

        if color_type == 'html':
            return self.html_color[color_selected]
        else:
            return self.rgb_color[color_selected]

    def display_metadata_pyqt_ui(self, view=None, save_it=True):

        if view is None:
            view = self.ui.image_view

        try:
            if view:
                pass
        except:
            return

        if self.metadata_pyqt_ui:
            view.removeItem(self.metadata_pyqt_ui)

        if not self.ui.metadata_checkbox.isChecked():
            return

        x0 = self.ui.metadata_position_x.value()
        y0 = self.ui.metadata_position_y.maximum() - self.ui.metadata_position_y.value()
        metadata_text = self.get_metadata_text()
        color = self.get_color(source='metadata', color_type='html')

        if self.ui.metadata_text_option.isChecked():

            text = pg.TextItem(html='<div style="text-align: center"><span style="color: ' + color + ';">' + metadata_text + '</span></div>')
            view.addItem(text)
            text.setPos(x0, y0)
            if save_it:
                self.metadata_pyqt_ui = text

        else: # we want a graph of the metadata

            data = np.array([1,2,5,7,9,10,9, 9, 8, 7,3,2,1,])
            graph = pg.PlotItem()
            graph.plot(data)
            view.addItem(graph)
            graph.setPos(x0, y0)
            if save_it:
                self.metadata_pyqt_ui = graph




    def get_metadata_text(self):
        """return the text and value of the metadata to display"""
        metadata_name = str(self.ui.manual_metadata_name.text())
        metadata_units = str(self.ui.manual_metadata_units.text())
        slider_index = self.ui.file_slider.value()
        metadata_value = str(self.ui.tableWidget.item(slider_index, 1).text())
        if metadata_name.strip() == '':
            return "{} {}".format(metadata_value, metadata_units)
        else:
            return "{}: {} {}".format(metadata_name, metadata_value, metadata_units)

    def get_scale_legend(self):
        real_scale_value = str(self.ui.scale_real_size.text())
        units_index_selected = self.ui.scale_units_combobox.currentIndex()
        html_units = self.list_scale_units['html'][units_index_selected]
        return "{} {}".format(real_scale_value, html_units)

    def display_scale_pyqt_ui(self, view=None, save_it=True):

        if view is None:
            view = self.ui.image_view

            try:
                if view:
                    pass
            except:
                return

        if self.scale_pyqt_ui:
            view.removeItem(self.scale_pyqt_ui)
            view.removeItem(self.scale_legend_pyqt_ui)

        if not self.ui.scale_checkbox.isChecked():
            return

        # scale
        thickness = self.ui.scale_thickness.value()
        size = self.ui.scale_size_spinbox.value()

        pos = []
        adj = []

        x0 = self.ui.scale_position_x.value()
        y0 = self.ui.scale_position_y.maximum() - self.ui.scale_position_y.value()

        one_edge = [x0, y0]
        if self.ui.scale_horizontal_orientation.isChecked():
            other_edge = [x0+size, y0]
            angle = 0
            legend_x0 = x0
            legend_y0 = y0
        else:
            other_edge = [x0, y0 + size]
            angle = 90
            legend_x0 = x0
            legend_y0 = y0 + np.int(size)

        pos.append(one_edge)
        pos.append(other_edge)
        adj.append([0, 1])

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = np.array(self.get_color(color_type='rgb', source='scale'))
        line_color[4] = thickness
        list_line_color = list(line_color)
        line_color =tuple(list_line_color)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        scale = pg.GraphItem()
        view.addItem(scale)
        scale.setData(pos=pos,
                      adj=adj,
                      pen=lines,
                      symbol=None,
                      pxMod=False)
        if save_it:
            self.scale_pyqt_ui = scale

        # legend
        legend = self.get_scale_legend()
        color = self.get_color(source='scale', color_type='html')
        text = pg.TextItem(html='<div style="text-align=center"><span style="color: ' + color + ';">' + \
                                legend + '</span></div>',
                           angle=angle)
        view.addItem(text)

        text.setPos(legend_x0, legend_y0)
        if save_it:
            self.scale_legend_pyqt_ui = text

    def display_image(self, recalculate_image=False):
        """display the image selected by the file slider"""
        DisplayImages(parent=self, recalculate_image=recalculate_image)

    def check_status_next_prev_image_button(self):
        """this will enable or not the prev or next button next to the slider file image"""
        current_slider_value = self.ui.file_slider.value()
        min_slider_value = self.ui.file_slider.minimum()
        max_slider_value = self.ui.file_slider.maximum()

        _prev = True
        _next = True

        if current_slider_value == min_slider_value:
            _prev = False
        elif current_slider_value == max_slider_value:
            _next = False

        self.ui.previous_image_button.setEnabled(_prev)
        self.ui.next_image_button.setEnabled(_next)

    def change_slider(self, offset=+1):
        self.ui.file_slider.blockSignals(True)
        current_slider_value = self.ui.file_slider.value()
        new_row_selected = current_slider_value + offset
        self.ui.image_slider_value.setText(str(new_row_selected))
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.ui.file_slider.blockSignals(False)


class ExportImages(object):

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


class Initializer(object):

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

        for _row, _file in enumerate(list_files_short_name):
            self.parent.ui.tableWidget.insertRow(_row)
            self.set_item_table(row=_row, col=0, value=_file)
            self.set_item_table(row=_row, col=1, value="N/A", editable=True)

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

        # hide the graph metadata size widgets
        self.parent.ui.metadata_graph_size_label.setVisible(False)
        self.parent.ui.metadata_graph_size_slider.setVisible(False)

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
        self.parent.ui.metadata_position_x.setMinimum(0)
        self.parent.ui.metadata_position_x.setMaximum(width)
        self.parent.ui.scale_position_y.setMaximum(height)
        self.parent.ui.metadata_position_y.setMaximum(height)
        self.parent.ui.metadata_position_y.setValue(height)

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


class DisplayImages(object):

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