import os
from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
import numpy as np

from __code import load_ui
from __code._utilities.table_handler import TableHandler

from __code.overlay_images.initialization import Initialization
from __code.overlay_images.event_handler import EventHandler
from __code.overlay_images.get import Get
from __code.overlay_images.export import Export


class InterfaceHandler:

    def __init__(self, working_dir=None, o_norm_high_res=None, o_norm_low_res=None):

        assert len(o_norm_low_res.data['sample']['file_name']) == len(o_norm_high_res.data['sample']['file_name'])

        o_interface = Interface(o_norm_high_res=o_norm_high_res,
                                o_norm_low_res=o_norm_low_res,
                                working_dir=working_dir)
        o_interface.show()

        self.o_interface = o_interface


class Interface(QMainWindow):

    SINGLE_OFFSET = 1  # pixels
    DOUBLE_OFFSET = 5  # pixels

    splitter_closed_state = None
    splitter_state = None

    horizontal_profile_plot = None
    vertical_profile_plot = None

    # {'file_high_reso_1.tif': {'offset': {'x': 0, 'y': 0},
    #                           'low_resolution_filename': 'file_low_reso_1.tif'},
    #  'file_high_reso_2.tif': {'offset': {'x': 0, 'y': 0},
    #                           'low_resolution_filename': 'file_low_reso_2.tif'},
    #   .... }
    dict_images_offset = None

    current_live_image = {'high_res': None, 'low_res': None, 'overlay': None}
    image_view = {'high_res': None, 'low_res': None, 'overlay': None}

    resize_and_overlay_images = []
    resize_hres_lres_images = {'hres': None, 'lres': None}
    resize_and_overlay_modes = []

    markers = {'high_res': {'1': {'x': 100, 'y': 50, 'ui': None, 'target_ui': None},
                            '2': {'x': 300, 'y': 50, 'ui': None, 'target_ui': None},
                            },
               'low_res':  {'1': {'x': 100, 'y': 50, 'ui': None, 'target_ui': None},
                            '2': {'x': 300, 'y': 50, 'ui': None, 'target_ui': None},
                            },
               'overlay': {'1': {'x': 500, 'y': 500, 'ui': None, 'target_ui': None, 'length': 200},
                           },
               'width': 50,
               'height': 50,
               'target': {'length': 10,
                          'border': 10,
                          'color': {'1': (255, 0, 0, 255, 1),
                                    '2': (0, 0, 255, 255, 1),
                                    'horizontal': (255, 0, 0, 255, 2),
                                    'vertical': (0, 0, 255, 255, 2)},
                          },
               }

    histogram_level = {'high_res': None, 'low_res': None, 'overlay': None}
    transparency = 0

    # if any of the current parameter is different from this, the EXPORT button becomes unavailable
    parameters_used_on_all_images = {'scaling_factor': 0,
                                     'xoffset': 0,
                                     'yoffset': 0}

    def __init__(self, parent=None, o_norm_high_res=None, o_norm_low_res=None, working_dir=None):

        self.o_norm_high_res = o_norm_high_res
        self.o_norm_low_res = o_norm_low_res
        self.working_dir = working_dir if working_dir else "./"

        self.high_res_image_height, self.high_res_image_width = np.shape(o_norm_high_res.data['sample']['data'][0])
        self.low_res_image_height, self.low_res_image_width = np.shape(o_norm_low_res.data['sample']['data'][0])
        self.rescaled_low_res_height, self.rescaled_low_res_width = None, None
        self.list_of_high_res_filename = o_norm_high_res.data['sample']['file_name']

        self.high_res_input_folder = os.path.dirname(o_norm_high_res.data['sample']['file_name'][0])
        self.low_res_input_folder = os.path.dirname(o_norm_low_res.data['sample']['file_name'][0])

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_overlay.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Overlay images with scaling")

        o_init = Initialization(parent=self)
        o_init.dictionaries()
        o_init.statusbar()
        o_init.widgets()
        o_init.pyqtgraph()
        o_init.markers()
        o_init.matplotlib()

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.select_row(row=0)
        self.markers_changed()

    # Event handler
    def update_previews(self, row_selected=-1):
        o_event = EventHandler(parent=self)
        o_event.update_views(row_selected=row_selected)

    def update_overlay_preview(self, row_selected=0):
        o_event = EventHandler(parent=self)
        o_event.update_overlay_view(row_selected=row_selected)

    def list_files_table_selection_changed(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        self.update_previews(row_selected=row_selected)

    def markers_changed(self):
        o_get = Get(parent=self)
        high_res_1_dict = o_get.marker_location(image_resolution='high_res', target_index='1')
        self.markers['high_res']['1']['x'] = high_res_1_dict['x']
        self.markers['high_res']['1']['y'] = high_res_1_dict['y']

        high_res_2_dict = o_get.marker_location(image_resolution='high_res', target_index='2')
        self.markers['high_res']['2']['x'] = high_res_2_dict['x']
        self.markers['high_res']['2']['y'] = high_res_2_dict['y']

        low_res_1_dict = o_get.marker_location(image_resolution='low_res', target_index='1')
        self.markers['low_res']['1']['x'] = low_res_1_dict['x']
        self.markers['low_res']['1']['y'] = low_res_1_dict['y']

        low_res_2_dict = o_get.marker_location(image_resolution='low_res', target_index='2')
        self.markers['low_res']['2']['x'] = low_res_2_dict['x']
        self.markers['low_res']['2']['y'] = low_res_2_dict['y']

        o_event = EventHandler(parent=self)
        o_event.update_target(image_resolution='high_res', target_index='1')
        o_event.update_target(image_resolution='high_res', target_index='2')

        o_event.update_target(image_resolution='low_res', target_index='1')
        o_event.update_target(image_resolution='low_res', target_index='2')

    def overlay_stack_of_images_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.overlay_stack_of_images_clicked()
        o_event.save_overlay_parameters()

    def scaling_factor_changed(self):
        self.manual_overlay_of_selected_image_only()

    def offset_changed(self):
        # checking value defined
        self._xoffset_value_to_add()
        self._yoffset_value_to_add()
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def xoffset_minus_clicked(self):
        self._xoffset_value_to_add(to_add=-self.SINGLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def xoffset_minus_minus_clicked(self):
        self._xoffset_value_to_add(to_add=-self.DOUBLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def xoffset_plus_clicked(self):
        self._xoffset_value_to_add(to_add=self.SINGLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def xoffset_plus_plus_clicked(self):
        self._xoffset_value_to_add(to_add=self.DOUBLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def yoffset_minus_clicked(self):
        self._yoffset_value_to_add(to_add=-self.SINGLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def yoffset_minus_minus_clicked(self):
        self._yoffset_value_to_add(to_add=-self.DOUBLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def yoffset_plus_clicked(self):
        self._yoffset_value_to_add(to_add=self.SINGLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def yoffset_plus_plus_clicked(self):
        self._yoffset_value_to_add(to_add=self.DOUBLE_OFFSET)
        self.manual_overlay_of_selected_image_only()
        self.check_export_button_status()

    def _xoffset_value_to_add(self, to_add=0):
        current_value = int(str(self.ui.xoffset_lineEdit.text()))
        new_value = current_value + to_add
        if new_value < 0:
            new_value = 0
        if new_value > self.rescaled_low_res_width - self.high_res_image_width:
            new_value = self.rescaled_low_res_width - self.high_res_image_width
        self.ui.xoffset_lineEdit.setText(str(new_value))

    def _yoffset_value_to_add(self, to_add=0):
        current_value = int(str(self.ui.yoffset_lineEdit.text()))
        new_value = current_value + to_add
        if new_value < 0:
            new_value = 0

        if new_value > self.rescaled_low_res_height - self.high_res_image_height:
            new_value = self.rescaled_low_res_height - self.high_res_image_height

        self.ui.yoffset_lineEdit.setText(str(new_value))

    def check_offset_manual_buttons_status(self):
        o_event = EventHandler(parent=self)
        o_event.check_offset_manual_button_status()
        o_event = EventHandler(parent=self)
        o_event.update_profile_plots()

    def manual_overlay_of_selected_image_only(self):
        o_event = EventHandler(parent=self)
        o_event.manual_overlay_of_selected_image_only()
        o_event = EventHandler(parent=self)
        o_event.update_profile_plots()
        self.check_export_button_status()

    def manual_overlay_of_all_images_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.manual_overlay_stack_of_images_clicked()
        o_event = EventHandler(parent=self)
        o_event.update_profile_plots()
        o_event.save_overlay_parameters()
        self.check_export_button_status()

    def tab_index_changed(self, tab_index):
        if tab_index == 0:
            self.splitter_state = self.ui.splitter_2.saveState()
            self.ui.splitter_2.setHandleWidth(0)
            self.ui.splitter_2.restoreState(self.splitter_closed_state)
        elif tab_index == 1:
            self.ui.splitter_2.setHandleWidth(10)
            self.ui.splitter_2.restoreState(self.splitter_state)
        o_event = EventHandler(parent=self)
        o_event.update_profile_plots()

    def profile_tool_clicked(self):
        _with_profile = self.ui.profile_tool_checkBox.isChecked()
        o_event = EventHandler(parent=self)
        if _with_profile:
            self.ui.splitter_2.setSizes([300, 500])
        else:
            self.ui.splitter_2.setSizes([800, 0])
        o_event.update_profile_markers_and_target(with_profile=_with_profile)
        o_event.update_profile_plots()

    def profile_region_moved(self):
        o_get = Get(parent=self)
        overlay_1_dict = o_get.marker_location(image_resolution='overlay', target_index='1')
        self.markers['overlay']['1']['x'] = overlay_1_dict['x']
        self.markers['overlay']['1']['y'] = overlay_1_dict['y']

        o_event = EventHandler(parent=self)
        o_event.update_profile_markers_and_target(with_profile=True)
        o_event.update_profile_plots()

    def transparency_slider_clicked(self):
        self.transparency = self.ui.transparency_slider.value()
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        o_event = EventHandler(parent=self)
        o_event.update_overlay_view(row_selected=row_selected)

    def transparency_slider_moved(self, value):
        self.transparency = value
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        o_event = EventHandler(parent=self)
        o_event.update_overlay_view(row_selected=row_selected)

    def transparency_checkBox_clicked(self):
        self.transparency = self.ui.transparency_slider.value()
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        o_event = EventHandler(parent=self)
        o_event.transparency_widgets_status()
        o_event.update_overlay_view(row_selected=row_selected)

    def export_overlaid_images_clicked(self):
        o_export = Export(parent=self)
        o_export.run()

    def check_export_button_status(self):
        o_event = EventHandler(parent=self)
        o_event.check_export_button_status()
