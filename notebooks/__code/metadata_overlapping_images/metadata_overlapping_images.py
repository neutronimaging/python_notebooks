from IPython.core.display import HTML
from IPython.core.display import display
import os
import copy
from PIL import Image
from qtpy.QtWidgets import QMainWindow, QFileDialog
from qtpy import QtGui

from __code import load_ui
from .initialization import Initializer
from .event_handler import MetadataTableHandler
from __code.metadata_overlapping_images.export_images import ExportImages
from .display import DisplayImages, DisplayScalePyqtUi, DisplayMetadataPyqtUi
from .table_loader import TableLoader
from __code.metadata_overlapping_images.advanced_table_handler import AdvancedTableHandler

from __code.metadata_overlapping_images import HELP_PAGE, LIST_FUNNY_CHARACTERS


class MetadataOverlappingImagesUi(QMainWindow):

    x_axis_column_index = 0
    y_axis_column_index = 2
    xy_axis_menu_logo = {'enable': u"\u2713  ",     # \u25CF (dark circle)
                         'disable': "     "}

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
    guide_table_width = [40, 400, 150, 150]

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
        o_initialization.pyqtgraph()
        o_initialization.parameters()
        o_initialization.statusbar()
        o_initialization.table()
        o_initialization.widgets()
        o_initialization.event()

        # display first images
        self.slider_file_changed(0)

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
        self.ui.scale_position_label.setEnabled(status)
        self.ui.scale_position_frame.setEnabled(status)
        o_display = DisplayScalePyqtUi(parent=self)
        o_display.run()

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
        key_selected = self.list_metadata[index]

        for row, _file in enumerate(self.data_dict['file_name']):
            o_image = Image.open(_file)
            o_dict = dict(o_image.tag_v2)
            value = o_dict[float(key_selected)]
            self.ui.tableWidget.item(row, column).setText("{}".format(value))

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

        o_display = DisplayMetadataPyqtUi(parent=self)
        o_display.run()

    def update_scale_pyqt_ui(self):
        if self.scale_pyqt_ui:
            self.ui.image_view.removeItem(self.scale_pyqt_ui)
        if self.scale_legend_pyqt_ui:
            self.ui.image_view.removeItem(self.scale_legend_pyqt_ui)

        o_display = DisplayScalePyqtUi(parent=self)
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
