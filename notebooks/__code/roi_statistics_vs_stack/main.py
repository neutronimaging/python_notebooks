from IPython.core.display import HTML
from IPython.display import display
import os
from qtpy.QtWidgets import QMainWindow


from __code import load_ui
from __code.file_folder_browser import FileFolderBrowser
from __code.roi_statistics_vs_stack.initialization import Initialization
from __code.roi_statistics_vs_stack.event_handler import EventHandler
from __code.roi_statistics_vs_stack.display import Display
from __code.roi_statistics_vs_stack.load import Load
from __code._utilities.file import ListMostDominantExtension
from __code._utilities.table_handler import TableHandler
from __code.roi_statistics_vs_stack.export import Export


class FileHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(FileHandler, self).__init__(working_dir=working_dir,
                                          next_function=self.display_status)

    def get_list_of_files(self):
        return self.list_images_ui.selected

    def select_folder(self):
        self.select_input_folder(instruction='Select folder containing images to process ...')

    def display_status(self, folder):
        o_list = ListMostDominantExtension(working_dir=folder)
        o_list.calculate()
        result = o_list.get_files_of_selected_ext()
        self.list_of_images = result.list_files
        nbr_images = str(len(self.list_of_images))
        display(HTML('<span style="font-size: 15px; color:blue">You have selected ' + nbr_images + ' images </span>'))


class ImageWindow(QMainWindow):

    list_of_images = None

    data_sub_dict = {'data': None,
                     'time_offset': 0,
                     'mean': None,
                     'max': None,
                     'min': None,
                     'std': None,
                     'median': None}

    x_axis = {'file_index': None,
              'time_offset': None}

    y_axis = {'mean': None,
              'max': None,
              'min': None,
              'std': None,
              'median': None}

    # {0: {'data': [], 'time_offset': 0},
    #  1: {'data': [], 'time_offset': 15},
    #  }
    data_dict = None
    live_image = None
    table_has_been_reset = False

    image_view_histogram_level = None

    roi_dict = {'x0': 200,
                'y0': 200,
                'width': 400,
                'height': 400}

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
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.select_row(new_value)

    def cancel_clicked(self):
        self.close()

    def plot_menu_changed(self):
        o_display = Display(parent=self)
        o_display.update_statistics_plot()

    def export_button_clicked(self):
        o_export = Export(parent=self)
        o_export.export()

    def closeEvent(self, event=None):
        pass

    def roi_changed(self):
        self.ui.export_button.setEnabled(False)
        if not self.table_has_been_reset:
            self.table_has_been_reset = True

            o_event = EventHandler(parent=self)
            o_event.reset_table_plot()

    def update_statistics_plot(self):
        o_display = Display(parent=self)
        o_display.update_statistics_plot()

    def initialize_ui(self):
        self.load_data()
        self.file_index_slider_changed(0)

        o_init = Initialization(parent=self)
        o_init.table()

        self.recalculate_table_clicked()
        self.update_statistics_plot()

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.select_row(0)

    def load_data(self):
        o_event = Load(parent=self)
        o_event.data()

    def table_selection_changed(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        self.ui.tableWidget.blockSignals(True)
        self.ui.horizontalSlider.setValue(row_selected)
        self.ui.tableWidget.blockSignals(False)

    def recalculate_table_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.recalculate_table()
        o_event.update_table()
        self.ui.export_button.setEnabled(True)
        self.table_has_been_reset = False
        self.ui.y_axis_groupBox.setEnabled(True)
        self.ui.x_axis_groupBox.setEnabled(True)
        self.plot_menu_changed()
