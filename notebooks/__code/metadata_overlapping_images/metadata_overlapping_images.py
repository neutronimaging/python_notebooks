from IPython.core.display import HTML
from IPython.core.display import display
import numpy as np
import os
import copy
import pyqtgraph as pg
from PIL import Image
from qtpy.QtWidgets import QMainWindow, QFileDialog
from qtpy import QtGui

from __code import load_ui
from __code.metadata_overlapping_images.export_images import Initializer
from __code.metadata_overlapping_images.export_images import MetadataTableHandler
from __code.metadata_overlapping_images.export_images import ExportImages
from __code.metadata_overlapping_images.export_images import DisplayImages
from __code.metadata_overlapping_images.export_images import TableLoader
from __code.metadata_overlapping_images.advanced_table_handler import AdvancedTableHandler

from __code.metadata_overlapping_images import HELP_PAGE, LIST_FUNNY_CHARACTERS


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
    graph_pyqt_ui = None

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

    rgba_color = {'white': (255, 255, 255, 255, None),
                   'red': (255, 0, 0, 255, None),
                   'green': (0, 255, 0, 255, None),
                   'blue': (0, 0, 255, 255, None),
                   'black': (0, 0, 0, 255, None)}

    rgb_color = {'white': (255, 255, 255),
                   'red': (255, 0, 0),
                   'green': (0, 255, 0),
                   'blue': (0, 0, 255),
                   'black': (0, 0, 0)}


    html_color = {'white': "#FFF",
                  'red': "#F00",
                  'green': "#0F0",
                  'blue': "#00F",
                  'black': "#000"}

    # ui of pop up window that allows to define metadata column value (format it)
    metadata_string_format_ui = None

    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        super(MetadataOverlappingImagesUi, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_images.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Metadata Overlapping Images")

        self.working_dir = working_dir
        self.data_dict = data_dict  # Normalization data dictionary  {'file_name': [],
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
        o_initialization.event()

        # display first images
        self.slider_file_changed(0)

    # ========================================================================================
    # MAIN UI EVENTs

    def metadata_table_right_click(self, position):
        # right click menu only for column 1
        if self.get_metadata_column_selected() != 1:
            return

        o_metadata_table = MetadataTableHandler(parent=self)
        o_metadata_table.right_click(position)

    def previous_image_button_clicked(self):
        self.change_slider(offset=-1)
        self.update_metadata_pyqt_ui()

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)
        self.update_metadata_pyqt_ui()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open(HELP_PAGE)

    def closeEvent(self, event=None):
        if self.metadata_string_format_ui:
            self.metadata_string_format_ui.close()

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
        self.ui.enable_graph_checkbox.setEnabled(status)

        if status:
            self.ui.graph_groupBox.setEnabled(self.ui.enable_graph_checkbox.isChecked())
        else:
            self.ui.graph_groupBox.setEnabled(False)

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

    def graph_position_moved(self, value):
        self.update_metadata_pyqt_ui()

    def graph_position_clicked(self):
        self.update_metadata_pyqt_ui()

    def graph_color_changed(self, value):
        self.update_metadata_pyqt_ui()

    def enable_graph_button_clicked(self, new_state):
        self.ui.graph_groupBox.setEnabled(self.ui.enable_graph_checkbox.isChecked())
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

    def table_cell_changed(self, row, column):
        self.update_metadata_pyqt_ui()

    def advanced_table_clicked(self):
        o_advanced = AdvancedTableHandler(parent=self)
        o_advanced.show()

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
        if self.graph_pyqt_ui:
            self.ui.image_view.removeItem(self.graph_pyqt_ui)

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
        elif source == 'graph':
            color_selected = self.ui.graph_color_combobox.currentText().lower()
        else:
            color_selected = self.ui.scale_color_combobox.currentText().lower()

        if color_type == 'html':
            return self.html_color[color_selected]
        elif color_type == 'rgba':
            return self.rgba_color[color_selected]
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

        if self.graph_pyqt_ui:
            view.removeItem(self.graph_pyqt_ui)

        if not self.ui.metadata_checkbox.isChecked():
            return

        x0 = self.ui.metadata_position_x.value()
        y0 = self.ui.metadata_position_y.maximum() - self.ui.metadata_position_y.value()
        metadata_text = self.get_metadata_text()
        color = self.get_color(source='metadata', color_type='html')

        text = pg.TextItem(html='<div style="text-align: center"><span style="color: ' + color + ';">' + metadata_text + '</span></div>')
        view.addItem(text)
        text.setPos(x0, y0)
        if save_it:
            self.metadata_pyqt_ui = text

        if self.ui.enable_graph_checkbox.isChecked():

            data = self.get_metadata_column()
            _view_box = pg.ViewBox(enableMouse=False)
            # _view_box.setBackgroundColor((100, 100, 100, 100))
            graph = pg.PlotItem(viewBox=_view_box)

            font_size = 8
            units = self.ui.manual_metadata_units.text()
            if units:
                y_axis_label = '<html><font color="{}" size="{}">{} ({})</font></html>'.format(color,
                                                                                               font_size,
                                                                                               self.ui.manual_metadata_name.text(),
                                                                                               units)
            else:
                y_axis_label = '<html><font color="{}" size="{}">{}</font></html>'.format(color,
                                                                                          font_size,
                                                                                          self.ui.manual_metadata_name.text())


            x_axis_label = '<p><font color="{}" size="{}">File Index</font></p>'.format(color,
                                                                                              font_size)

            graph.setLabel('left', text=y_axis_label)
            graph.setLabel('bottom', text=x_axis_label)

            _size = self.ui.metadata_graph_size_slider.value()
            graph.setFixedWidth(_size)
            graph.setFixedHeight(_size)
            color_pen = self.get_color(source='graph', color_type='rgb_color')
            graph.plot(data, pen=color_pen)

            # highlight current file
            current_index = self.ui.file_slider.value()
            _pen = pg.mkPen((255, 0, 0), width=4)

            graph.plot(x=[current_index], y=[data[current_index]],
                       pen=_pen,
                       symboBrush=(255, 0, 0),
                       symbolPen='w')
            _inf_line = pg.InfiniteLine(current_index, pen=_pen)
            graph.addItem(_inf_line)

            x0 = self.ui.graph_position_x.value()
            y0 = self.ui.graph_position_y.maximum() - self.ui.graph_position_y.value()

            view.addItem(graph)
            graph.setPos(x0, y0)

            if save_it:
                self.graph_pyqt_ui = graph

    def get_raw_metadata_column(self):
        data = []
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.ui.tableWidget.item(_row, 1).text())
            data.append(_row_str)

        return data

    def get_metadata_column(self):
        data = []
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.ui.tableWidget.item(_row, 1).text())
            split_row_str = _row_str.split(":")
            if len(split_row_str) == 1:
                _row_str = split_row_str[0]
            else:
                _row_str = split_row_str[1]
            try:
                _row_value = np.float(_row_str)
            except:
                self.ui.statusbar.showMessage("Error Displaying Metadata Graph!", 10000)
                self.ui.statusbar.setStyleSheet("color: red")
                return []

            data.append(_row_value)

        return data

    def get_metadata_column_selected(self):
        selection = self.ui.tableWidget.selectedRanges()[0]
        return selection.leftColumn()

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

        line_color = np.array(self.get_color(color_type='rgba', source='scale'))
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
