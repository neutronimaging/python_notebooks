from IPython.core.display import HTML
from IPython.core.display import display
import os
import copy
from qtpy.QtWidgets import QMainWindow, QFileDialog
from qtpy import QtGui
from collections import OrderedDict

from __code import load_ui
from .initialization import Initializer
from .event_handler import MetadataTableHandler
from __code.metadata_overlapping_images.export_images import ExportImages
from .display import DisplayImages, DisplayScalePyqtUi, DisplayMetadataPyqtUi
from .export_table import ExportTable

from __code.metadata_overlapping_images import HELP_PAGE


class MetadataOverlappingImagesUi(QMainWindow):

    x_axis_column_index = 0
    y_axis_column_index = 2
    xy_axis_menu_logo = {'enable': u"\u2713  ",     # \u25CF (dark circle)
                         'disable': "     "}

    metadata_operation = {0: {"first_part_of_string_to_remove": "",
                              "last_part_of_string_to_remove": "",
                              "math_1": "+",
                              "value_1": "",
                              "math_2": "+",
                              "value_2": "",
                              "index_of_metadata": -1,
                              },
                          2: {"first_part_of_string_to_remove": "",
                              "last_part_of_string_to_remove": "",
                              "math_1": "+",
                              "value_1": "",
                              "math_2": "+",
                              "value_2": "",
                              "index_of_metadata": -1,
                              },
                          3: {"first_part_of_string_to_remove": "",
                              "last_part_of_string_to_remove": "",
                              "math_1": "+",
                              "value_1": "",
                              "math_2": "+",
                              "value_2": "",
                              "index_of_metadata": -1,
                              },
                          }

    data_dict = {}
    data_dict_raw = {}
    timestamp_dict = {}
    default_scale_roi = None

    rotation_angle = 0
    histogram_level = []

    # scale pyqtgraph
    scale_pyqt_ui = None
    scale_legend_pyqt_ui = None

    metadata1_pyqt_ui = None # metadata 1 text
    metadata2_pyqt_ui = None # metadata 2 text

    graph_pyqt_ui = None

    # size of tables
    guide_table_width = [40, 400, 150, 150]

    live_image = []
    display_ui = []

    # guide and profile pg ROIs
    list_guide_pyqt_roi = list()
    list_profile_pyqt_roi = list()
    list_table_widget_checkbox = list()

    list_metadata = []
    dict_list_metadata = OrderedDict() #  {0: '10', 1: 'hfir', ...}
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

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
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
        o_initialization.pyqtgraph()
        o_initialization.parameters()
        o_initialization.statusbar()
        o_initialization.table()
        o_initialization.widgets()
        o_initialization.event()

        # display first images
        self.slider_file_changed(0)
        self.text_metadata_1_enable_pressed(self.ui.checkBox.isChecked())
        self.text_metadata_2_enable_pressed(self.ui.checkBox_2.isChecked())

    # ========================================================================================
    # MAIN UI EVENTs

    def metadata_table_right_click(self, position):
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
        self.ui.scale_position_frame.setEnabled(status)
        o_display = DisplayScalePyqtUi(parent=self)
        o_display.run()

    def metadata_checkbox_clicked(self, status):
        self.ui.metadata_groupbox.setEnabled(status)
        self.ui.metadata_position_frame.setEnabled(status)
        self.ui.enable_graph_checkbox.setEnabled(status)
        self.ui.text_graph_tabWidget.setEnabled(status)
        self.ui.toolBox.setEnabled(status)

        if status:
            self.ui.graph_groupBox.setEnabled(self.ui.enable_graph_checkbox.isChecked())
        else:
            self.ui.graph_groupBox.setEnabled(False)

        o_display = DisplayMetadataPyqtUi(parent=self)
        o_display.run()

    def select_metadata_checkbox_clicked(self, status):
        self.ui.select_metadata_combobox.setEnabled(status)
        self.update_metadata_pyqt_ui()

    def font_size_slider_pressed(self):
        self.update_metadata_pyqt_ui()

    def font_size_slider_moved(self, value):
        self.update_metadata_pyqt_ui()

    def graph_font_size_slider_pressed(self):
        self.update_metadata_pyqt_ui()

    def graph_font_size_slider_moved(self, value):
        self.update_metadata_pyqt_ui()

    def metadata_list_changed(self, index, column):
        o_event = MetadataTableHandler(parent=self)
        o_event.metadata_list_changed(index, column)

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

    def metadata2_position_moved(self, new_value):
        self.update_metadata_pyqt_ui()

    def metadata2_position_clicked(self):
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

    def graph_axis_label_changed(self, new_value):
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

    def export_table_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=os.path.dirname(self.working_dir),
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        QtGui.QGuiApplication.processEvents()
        if _export_folder:
            o_export = ExportTable(parent=self,
                                   export_folder=_export_folder)
            o_export.run()


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

    # def import_table_pressed(self):
    #     _table_file = QFileDialog.getOpenFileName(self,
    #                                               directory=os.path.dirname(self.working_dir),
    #                                               caption="Select Input File")
    #     QtGui.QGuiApplication.processEvents()
    #
    #     if type(_table_file) is tuple:
    #         _table_file = _table_file[0]
    #
    #     if _table_file:
    #         o_import = TableLoader(parent=self,
    #                                filename=str(_table_file))
    #         o_import.load_table()
    #         o_import.populate()
    #         self.update_metadata_pyqt_ui()

    def enable_graph_button_clicked(self, new_state):
        self.ui.graph_groupBox.setEnabled(new_state)
        self.ui.metadata_position_frame_3.setEnabled(new_state)
        self.ui.graph_position_y.setEnabled(new_state)
        self.ui.graph_position_x.setEnabled(new_state)
        self.ui.label_15.setEnabled(new_state)
        self.ui.label_16.setEnabled(new_state)
        self.update_metadata_pyqt_ui()

    def display_red_vertical_marker_clicked(self):
        self.update_metadata_pyqt_ui()

    def text_metadata_1_enable_pressed(self, status):
        self.ui.metadata_position_frame.setEnabled(status)
        self.ui.metadata_position_x.setEnabled(status)
        self.ui.metadata_position_y.setEnabled(status)
        self.ui.label_10.setEnabled(status)
        self.ui.label_11.setEnabled(status)
        self.ui.label_14.setEnabled(status)
        self.ui.font_size_slider.setEnabled(status)
        self.ui.prefix_label_1.setEnabled(status)
        self.ui.suffix_label_1.setEnabled(status)
        self.ui.prefix_lineEdit_1.setEnabled(status)
        self.ui.suffix_lineEdit_1.setEnabled(status)
        self.ui.metadata_1_name_groupBox.setEnabled(status)
        self.update_metadata_pyqt_ui()

    def text_metadata_2_enable_pressed(self, status):
        self.ui.metadata_position_frame_2.setEnabled(status)
        self.ui.metadata_position_x_2.setEnabled(status)
        self.ui.metadata_position_y_2.setEnabled(status)
        self.ui.label_18.setEnabled(status)
        self.ui.label_19.setEnabled(status)
        self.ui.label_20.setEnabled(status)
        self.ui.font_size_slider_2.setEnabled(status)
        self.ui.prefix_label_2.setEnabled(status)
        self.ui.suffix_label_2.setEnabled(status)
        self.ui.prefix_lineEdit_2.setEnabled(status)
        self.ui.suffix_lineEdit_2.setEnabled(status)
        self.ui.metadata_2_name_groupBox.setEnabled(status)
        self.update_metadata_pyqt_ui()

    def metadata_1_suffix_prefix_changed(self, new_text):
        self.update_metadata_pyqt_ui()

    def metadata_2_suffix_prefix_changed(self, new_text):
        self.update_metadata_pyqt_ui()

    # ========================================================================================

    def update_metadata_pyqt_ui(self):
        o_display = DisplayMetadataPyqtUi(parent=self)
        o_display.clear_pyqt_items()
        o_display.run()

    def update_scale_pyqt_ui(self):
        # if self.scale_pyqt_ui:
        #     self.ui.image_view.removeItem(self.scale_pyqt_ui)
        # if self.scale_legend_pyqt_ui:
        #     self.ui.image_view.removeItem(self.scale_legend_pyqt_ui)
        o_display = DisplayScalePyqtUi(parent=self)
        o_display.clear_pyqt_items()
        o_display.run()

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
