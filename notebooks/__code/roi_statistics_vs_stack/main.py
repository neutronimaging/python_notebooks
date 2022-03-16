from IPython.core.display import HTML
from IPython.display import display
import numpy as np
import os
import numbers
from qtpy.QtWidgets import QMainWindow


from __code import load_ui
from __code.file_folder_browser import FileFolderBrowser
from __code.roi_statistics_vs_stack.initialization import Initialization
from __code.roi_statistics_vs_stack.event_handler import EventHandler
from __code.roi_statistics_vs_stack.display import Display
from __code.roi_statistics_vs_stack.table import Table
from __code.roi_statistics_vs_stack.load import Load


class FileHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(FileHandler, self).__init__(working_dir=working_dir,
                                          next_function=self.display_status)

    def get_list_of_files(self):
        return self.list_images_ui.selected

    def select_images(self):
        self.select_input_folder(instruction='Select folder containing images to process ...')

    def display_status(self, list_of_files):
        self.list_of_images = list_of_files
        nbr_images = str(len(list_of_files))
        display(HTML('<span style="font-size: 15px; color:blue">You have selected ' + nbr_images + ' images </span>'))


class ImageWindow(QMainWindow):

    list_of_images = None

    # {0: {'data': [], 'time_offset': 0},
    #  1: {'data': [], 'time_offset': 15},
    #  }
    data_dict = None


    stack = []
    integrated_stack = []
    working_folder = ''

    def __init__(self, parent=None, list_of_images=None):

        self.list_of_images = list_of_images
        self.working_folder = os.path.dirname(list_of_images[0])

        super(ImageWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_roi_statistics_vs_stack.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select ROI to display profile over all images.")

        o_init = Initialization(parent=self)
        o_init.all()

    def file_index_slider_changed(self, new_value):
        o_display = Display(parent=self)
        o_display.update_image_view(slider_value=new_value)
        self.ui.slider_value.setText(str(new_value))

    def cancel_clicked(self):
        self.close()

    def plot_menu_changed(self):
        print("plot menu changed")

    def export_button_clicked(self):
        print("export button clicked")

    def closeEvent(self, event=None):
        pass

    def done_button_clicked(self):
        print("done button clicked")

    def update_table(self):
        o_table = Table(parent=self)
        o_table.update()

    def initialize_ui(self):
        self.load_data()
        self.file_index_slider_changed(0)

        o_init = Initialization(parent=self)
        o_init.table()

    def load_data(self):
        o_event = Load(parent=self)
        o_event.data()

    def update_plot(self):
        self.update_x_axis()
        self.plot()

    def roi_changed(self):
        pass
        # region = self.ui.roi.getArraySlice(self.integrated_stack,
        #                                    self.ui.image_view.imageItem)
        # x0 = region[0][0].start
        # x1 = region[0][0].stop - 1
        # y0 = region[0][1].start
        # y1 = region[0][1].stop - 1
        #
        # mean_selection = [_data[x0:x1, y0:y1].mean() for _data in self.stack]
        # self.y_axis['data'] = mean_selection
        # self.plot()

