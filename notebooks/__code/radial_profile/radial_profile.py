from IPython.core.display import HTML
from IPython.display import display
from qtpy.QtWidgets import QMainWindow, QFileDialog, QApplication
from qtpy import QtCore, QtGui
import numpy as np
import os

from sectorizedradialprofile.calculate_radial_profile import CalculateRadialProfile

from __code import load_ui
from __code import file_handler
from __code.color import Color
from __code.radial_profile.event_handler import EventHandler
from __code.radial_profile.initialization import Initialization
from __code.radial_profile.display import Display
from __code._utilities.metadata_handler import MetadataHandler


class RadialProfile:

    nbr_files = 0
    images_dimension = {'height': 0,
                        'width': 0}

    working_data = []
    working_dir = ''
    list_images = []
    profile_data = []

    def __init__(self, parent_ui=None, data=None, list_files=None):
        self.working_data = data
        self.parent_ui = parent_ui
        self.list_images = list_files

        self.short_list_files = [os.path.basename(_file) for _file in list_files]

        color = Color()
        self.list_rgb_profile_color = color.get_list_rgb(nbr_color=len(self.working_data))

    def calculate(self, center=None, angle_range=None, max_radius=None):

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self.center = center
        self.angle_range = angle_range
        self.max_radius = max_radius

        center = tuple([center['x0'], center['y0']])
        angle_range = tuple([angle_range['from'], angle_range['to']])

        nbr_files = len(self.working_data)

        self.parent_ui.eventProgress.setMinimum(1)
        self.parent_ui.eventProgress.setMaximum(nbr_files)
        self.parent_ui.eventProgress.setValue(1)
        self.parent_ui.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        _array_profile = []

        self.parent_ui.ui.profile_plot.clear()
        try:
            self.parent_ui.ui.profile_plot.scene().removeItem(self.parent_ui.legend)
        except Exception as e:
            pass
        self.parent_ui.legend = self.parent_ui.ui.profile_plot.addLegend()
        QtGui.QGuiApplication.processEvents()

        for _index in np.arange(nbr_files):
            o_calculation = CalculateRadialProfile(data=self.working_data[_index])
            o_calculation.add_params(center=center,
                                     angle_range=angle_range,
                                     radius=max_radius)
            o_calculation.calculate()

            _short_file_name = self.short_list_files[_index]

            _df = o_calculation.radial_profile

            radius = np.array(_df.index)
            profile = np.array(_df["mean"])

            _array_profile.append(profile)
            self.parent_ui.eventProgress.setValue(_index+1)

            # display
            _color = self.list_rgb_profile_color[_index]
            self.plot(radius, profile, _short_file_name, _color)

            QtGui.QGuiApplication.processEvents()

        QtGui.QGuiApplication.processEvents()
        self.parent_ui.eventProgress.setVisible(False)
        self.profile_data = _array_profile

        QApplication.restoreOverrideCursor()

    def plot(self, xaxis, data, label, color):
        self.parent_ui.ui.profile_plot.plot(xaxis, data, name=label, pen=color)
        self.parent_ui.ui.profile_plot.setLabel('left', "Average counts")
        self.parent_ui.ui.profile_plot.setLabel('bottom', "Radius (pixel)")

    def export(self, output_folder=''):
        if output_folder:
            for _index, _file in enumerate(self.list_images):

                time_stamp_of_that_file = MetadataHandler.get_time_stamp(file_name=_file)
                [input_image_base_name, ext] = os.path.splitext(os.path.basename(_file))
                output_file_name = os.path.join(output_folder,
                                                input_image_base_name + '_profile_c_x{}_y{}_angle_{}_to_{}'.format(
                                                        self.center['x0'], self.center['y0'],
                                                        self.angle_range['from'], self.angle_range['to']))
                if self.max_radius:
                    output_file_name += "_max_radius_of_{}_pixels".format(self.max_radius)
                output_file_name += ".txt"
                output_file_name = os.path.abspath(output_file_name)

                text = ["# source image: {}".format(_file)]
                text.append("# timestamp: {}".format(time_stamp_of_that_file))
                text.append("# center [x0, y0]: [{},{}]".format(self.center['x0'], self.center['y0']))
                text.append(
                    "# angular range from {}degrees to {}degrees".format(self.angle_range['from'],
                                                                         self.angle_range['to']))
                text.append('')
                text.append('#pixel_from_center, Average_counts')
                data = list(zip(np.arange(len(self.profile_data[_index])), self.profile_data[_index]))

                file_handler.make_ascii_file(metadata=text, data=data, output_file_name=output_file_name)

        self.parent_ui.ui.statusbar.showMessage("Profiles Exported in {}!".format(output_folder), 10000)
        self.parent_ui.ui.statusbar.setStyleSheet("color: green")


class SelectRadialParameters(QMainWindow):

    grid_size = 200
    live_data = []

    sector_g = None

    from_angle_line = None
    to_angle_line = None

    max_radius_item = None

    guide_color_slider = {'red': 255,
                          'green': 0,
                          'blue': 255,
                          'alpha': 255}

    sector_range = {'from': 0,
                    'to': 90}

    corners = {'top_right': np.NaN,
               'bottom_right': np.NaN,
               'bottom_left': np.NaN,
               'top_left': np.NaN}

    hLine = None
    vLine = None

    height = np.NaN
    width = np.NaN

    angle_0 = None
    angle_90 = None
    angle_180 = None
    angle_270 = None

    histogram_level = []

    profile_data = []
    legend = None

    dict_files_timestamp = {}

    # def __init__(self, parent=None, o_profile=None):
    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Select the center of the circle and the angular '
                     'sector in the UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        # o_profile.load_images()
        self.list_images = data_dict['file_name']
        self.working_data = data_dict['data']
        self.metadata = data_dict['metadata']
        self.working_dir = working_dir
        # self.rotated_working_data = data_dict['data']
        [self.height, self.width] = np.shape(self.working_data[0])

        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_radial_profile.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Define center and sector of profile")

        o_init = Initialization(parent=self)
        o_init.statusbar()
        o_init.pyqtgraph()
        o_init.widgets()

        o_display = Display(parent=self)
        o_display.grid()
        self.file_index_changed()
        o_init.crosshair()

        self.apply_clicked()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/tutorial/notebooks/radial_profile/")

    def grid_slider_moved(self, value):
        self.grid_size_changed()

    def grid_slider_pressed(self):
        self.grid_size_changed()

    def sector_radio_button_changed(self):
        o_event = EventHandler(parent=self)
        o_event.sector_radio_button_changed()

    # from and to angles sliders
    def sector_from_angle_moved(self, value):
        self.ui.sector_from_value.setText(str(value))
        self.check_from_to_angle(do_not_touch='from')
        self.sector_changed()

    def sector_to_angle_moved(self, value):
        self.ui.sector_to_value.setText(str(value))
        self.check_from_to_angle(do_not_touch='to')
        self.sector_changed()

    def sector_from_angle_clicked(self):
        self.check_from_to_angle(do_not_touch='from')
        self.sector_changed()

    def sector_to_angle_clicked(self):
        self.check_from_to_angle(do_not_touch='to')
        self.sector_changed()

    def get_image_dimension(self, array_image):
        if len(np.shape(array_image)) > 2:
            return np.shape(array_image[0])
        else:
            return np.shape(array_image)

    def get_selected_image(self, file_index):

        if len(np.shape(self.working_data)) > 2:
            return self.working_data[file_index]
        else:
            return self.working_data

    def sector_changed(self):
        o_event = EventHandler(parent=self)
        o_event.circle_center_changed()
        self.apply_clicked()

    def grid_size_changed(self):
        if self.line_view_binning:
            self.ui.image_view.removeItem(self.line_view_binning)
        o_display = Display(parent=self)
        o_display.grid()

    def calculate_profiles_clicked(self):
        o_profile = RadialProfile(parent_ui=self,
                                  data=self.working_data,
                                  list_files=self.list_images)
        radius = self.ui.max_radius_slider.value() if self.ui.max_radius_radioButton.isChecked() else None
        o_profile.calculate(center=self.center,
                            angle_range=self.angle_range,
                            max_radius=radius)

        self.profile_data = o_profile.profile_data
        self.o_profile = o_profile
        self.check_export_button_status()

    def export_profiles_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        QApplication.processEvents()
        if _export_folder:
            o_profile = self.o_profile
            o_profile.export(output_folder=_export_folder)

    # Main functions  -----------------------

    def check_export_button_status(self):
        if self.profile_data == []:
            status = False
        else:
            status = True
        self.ui.export_profiles_button.setEnabled(status)

    def check_from_to_angle(self, do_not_touch='from'):
        from_angle = self.ui.from_angle_slider.value()
        to_angle = self.ui.to_angle_slider.value()

        if do_not_touch == 'from':
            if to_angle < from_angle:
                self.ui.to_angle_slider.setValue(from_angle)
                self.ui.sector_to_value.setText(str(from_angle))
        else:
            if from_angle > to_angle:
                self.ui.from_angle_slider.setValue(to_angle)
                self.ui.sector_from_value.setText(str(to_angle))

    def manual_circle_center_changed(self):
        new_x0 = np.int(self.vLine.value())
        self.ui.circle_x.setText("{}".format(new_x0))

        new_y0 = np.int(self.hLine.value())
        self.ui.circle_y.setText("{}".format(new_y0))

        o_event = EventHandler(parent=self)
        o_event.circle_center_changed()
        o_event.update_max_radius_value()

    def guide_color_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.guide_color_changed()

    def guide_color_released(self):
        o_event = EventHandler(parent=self)
        o_event.guide_color_changed()

    def guide_color_changed(self, index):
        o_event = EventHandler(parent=self)
        o_event.guide_color_changed()

    def apply_clicked(self):
        _center = {}
        _center['x0'] = np.float(str(self.ui.circle_x.text()))
        _center['y0'] = np.float(str(self.ui.circle_y.text()))
        self.center = _center

        _angle_range = {}
        if self.ui.sector_full_circle.isChecked():
            _from_angle = 0
            _to_angle = 360
        else:
            _from_angle = np.float(self.ui.from_angle_slider.value())
            _to_angle = np.float(self.ui.to_angle_slider.value())
        _angle_range['from'] = _from_angle
        _angle_range['to'] = _to_angle
        self.angle_range = _angle_range

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        o_event = EventHandler(parent=self)
        o_event.file_index_changed()

    def max_radius_button_clicked(self):
        is_max_radius_selected = self.ui.max_radius_radioButton.isChecked()
        self.ui.max_radius_slider.setEnabled(is_max_radius_selected)
        o_event = EventHandler(parent=self)
        o_event.max_radius_handler(is_max_radius_selected=is_max_radius_selected)

    def max_radius_slider_pressed(self):
        o_event = EventHandler(parent=self)
        o_event.update_max_radius_item()

    def max_radius_slider_changed(self, value):
        o_event = EventHandler(parent=self)
        o_event.update_max_radius_item()

    def display_image(self, image):
        image = np.transpose(image)
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")
