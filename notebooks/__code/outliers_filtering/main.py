from IPython.core.display import HTML
from IPython.display import display
import os
from qtpy.QtWidgets import QMainWindow

from __code import load_ui

from __code.file_folder_browser import FileFolderBrowser
from __code.decorators import wait_cursor
from __code.outliers_filtering.initialization import Initialization
from __code.outliers_filtering.event_handler import EventHandler
from __code.outliers_filtering.export import Export


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

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        self.list_files = list_of_files
        self.working_dir = os.path.dirname(list_of_files[0])

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

    def table_selection_changed(self):
        o_event = EventHandler(parent=self)
        o_event.table_selection_changed()

    def algorithm_changed(self):
        o_event = EventHandler(parent=self)
        o_event.algorithm_changed()

    def mouse_moved_in_any_image(self, evt, image='raw'):
        o_event = EventHandler(parent=self)
        o_event.mouse_moved_in_any_image(position=evt[0], image=image)

    @wait_cursor
    def filtering_coefficient_changed(self):
        self.fill_table()
        self.slider_moved()

    def mouse_moved_in_raw_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='raw')

    def mouse_moved_in_filtered_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='filtered')

    def correct_all_images_clicked(self):
        o_export = Export(parent=self)
        o_export.export()

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
