from IPython.core.display import HTML
from IPython.display import display
import os
import numpy as np
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui

from __code import load_ui

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser
from __code.decorators import wait_cursor
from __code.outliers_filtering.initialization import Initialization
from __code.outliers_filtering.event_handler import EventHandler


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir,
                                               next_function=self.display_status)

    def get_list_of_files(self):
        return self.list_images_ui.selected

    def select_all_images(self):
        self.select_images(instruction='Select all tiff or Fits Images to process ...')

    def display_status(self, list_of_files):
        nbr_images = str(len(list_of_files))
        display(HTML('<span style="font-size: 15px; color:blue">You have selected ' + nbr_images + ' images </span>'))


class Interface(QMainWindow):

    live_data = []
    default_filtering_coefficient_value = 0.1

    table_columns_size = [300, 200, 200, 200, 200]

    raw_histogram_level = []
    filtered_histogram_level = []
    diff_filtered_histogram_level = []

    nbr_histo_bins = 2000

    live_raw_image = []
    live_filtered_image = []
    live_diff_image = []

    # list of arrays of raw and filtered data
    # data = {'file1': {'raw': [], 'filtered': []},
    #         'file2': {'raw': [], 'filtered': []},
    #         ... }
    data = {}

    # ['file1', 'file2', ...]
    list_short_file_name = None

    # ['/HFIR/CG1D/.../file1', '/HFIR/CG1D/...'file2']
    list_files = None

    image_size = None

    def __init__(self, parent=None, list_of_files=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.list_files = list_of_files

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_outliers_filtering_tool.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        o_init = Initialization(parent=self)
        o_init.pyqtgraph()
        o_init.widgets()
        o_init.table()
        o_init.statusbar()

        self.algorithm_changed()
        self.table_selection_changed()

        # self.slider_moved()
        # self.fill_table()

    def table_selection_changed(self):
        o_event = EventHandler(parent=self)
        o_event.table_selection_changed()

    def algorithm_changed(self):
        o_event = EventHandler(parent=self)
        o_event.algorithm_changed()

    def __get_filtering_coefficient_value(self):
        """retrieve the gamma filtered value and make sure it's a float number and
        it stays between 0 and 1"""
        value = self.ui.filtering_coefficient_value.text()
        try:
            float_value = np.float(value)
        except:
            self.ui.filtering_coefficient_value.setText(str(self.default_filtering_coefficient_value))
            return self.default_filtering_coefficient_value

        if float_value < 0:
            float_value = 0
            self.ui.filtering_coefficient_value.setText(str(float_value))
        elif float_value > 1:
            float_value = 1
            self.ui.filtering_coefficient_value.setText(str(float_value))

        return float_value

    def fill_table(self):
        raw_image_size = self.image_size
        total_nbr_pixels = raw_image_size[0] * raw_image_size[1]

        for _row, _file in enumerate(self.list_files):

            o_norm = Normalization()
            o_norm.load(file=_file, auto_gamma_filter=False, manual_gamma_filter=True, manual_gamma_threshold=self.__get_filtering_coefficient_value())
            _raw_data = o_norm.data['sample']['data']
            nbr_pixel_corrected = self.get_number_pixel_gamma_corrected(data=_raw_data)

            # number of pixel corrected
            _item = QtGui.QTableWidgetItem("{}/{}".format(nbr_pixel_corrected, total_nbr_pixels))
            self.ui.tableWidget.setItem(_row, 1, _item)

            # percentage of pixel corrected
            _item = QtGui.QTableWidgetItem("{:.02f}%".format(nbr_pixel_corrected*100/total_nbr_pixels))
            self.ui.tableWidget.setItem(_row, 2, _item)

    # def get_number_pixel_gamma_corrected(self, data=[]):
    #     filtering_coefficient = self.__get_filtering_coefficient_value()
    #     mean_counts = np.mean(data)
    #     _data = np.copy(data)
    #     gamma_indexes = np.where(filtering_coefficient * _data > mean_counts)
    #     return len(gamma_indexes[0])

    def mouse_moved_in_any_image(self, evt, image='raw'):
        pos = evt[0]

        if image == 'raw':
            image_view = self.ui.raw_image_view
        elif image == 'filtered':
            image_view = self.ui.filtered_image_view
        else:
            image_view = self.ui.diff_image_view

        if image_view.view.sceneBoundingRect().contains(pos):

            [height, width] = self.image_size

            #mouse_point = self.ui.raw_image_view.view.vb.mapSceneToView(pos)
            mouse_point = image_view.view.getViewBox().mapSceneToView(pos)
            mouse_x = int(mouse_point.x())
            mouse_y = int(mouse_point.y())

            if (mouse_x >= 0 and mouse_x < width) and \
                    (mouse_y >= 0 and mouse_y < height):
                self.x_value.setText(str(mouse_x))
                self.y_value.setText(str(mouse_y))

                _raw_value = self.live_raw_image[mouse_x, mouse_y]
                _filtered_value = self.live_filtered_image[mouse_x, mouse_y]

                self.raw_value.setText("{:.02f}".format(_raw_value))
                self.filtered_value.setText("{:.02f}".format(_filtered_value))

                self.raw_hLine.setPos(mouse_point.y())
                self.raw_vLine.setPos(mouse_point.x())
                self.filtered_hLine.setPos(mouse_point.y())
                self.filtered_vLine.setPos(mouse_point.x())

            else:
                self.x_value.setText("N/A")
                self.y_value.setText("N/A")
                self.raw_value.setText("N/A")
                self.filtered_value.setText("N/A")

    @wait_cursor
    def filtering_coefficient_changed(self):
        self.fill_table()
        self.slider_moved()

    def mouse_moved_in_raw_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='raw')

    def mouse_moved_in_filtered_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='filtered')

    def slider_clicked(self):
        self.slider_moved()

    def slider_moved(self):
        slider_position = self.ui.file_index_slider.value()

        self.display_raw_image(file_index=slider_position-1)
        self.display_corrected_image(file_index=slider_position-1)
        self.ui.file_index_value.setText(str(slider_position))
        self.reset_states()

    def reset_states(self):
        _state = self.state_of_raw

        # raw
        _view = self.ui.raw_image_view.getView()
        _view_box = _view.getViewBox()
        _view_box.setState(_state)

        # filtered
        _view = self.ui.filtered_image_view.getView()
        _view_box = _view.getViewBox()
        _view_box.setState(_state)

    def apply_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        file_index = self.ui.slider.value()
        new_live_image = self.list_data[file_index]
        self.ui.image_view.setImage(new_live_image)
        self.ui.file_name.setText(self.list_files[file_index])

    def help_clicked(self):
        import webbrowser
        webbrowser.open('https://neutronimaging.pages.ornl.gov/tutorial/notebooks/gamma_filtering_tool/')

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, event=None):
        print("Leaving Parameters Selection UI")
