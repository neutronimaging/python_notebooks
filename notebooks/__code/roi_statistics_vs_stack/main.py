from IPython.core.display import HTML
from IPython.display import display
import numpy as np
import os
import numbers
from qtpy.QtWidgets import QMainWindow

from NeuNorm.normalization import Normalization

from __code import load_ui
from __code.file_folder_browser import FileFolderBrowser
from __code.roi_statistics_vs_stack.initialization import Initialization


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
        o_init.pyqtgraph()
        o_init.splitter()

        # [self.nbr_files, height, width] = np.shape(self.stack)
        # self.integrated_stack = self.stack.sum(axis=0)
        #
        # self.initialize_pyqtgraph()
        # self.init_label()
        #
        # self.display_image()
        # self.update_x_axis()
        # self.roi_changed()

    def load_data(self):
        working_folder = self.working_folder
        o_norm = Normalization()
        o_norm.load(folder=working_folder, notebook=True)
        self.stack = np.array(o_norm.data['sample']['data'])

    def update_plot(self):
        self.update_x_axis()
        self.plot()


    def display_image(self):
        self.ui.image_view.setImage(self.integrated_stack)

    def plot(self):
        x_axis_data = self.x_axis['data']
        x_axis_label = self.x_axis['label']
        
        y_axis_data = self.y_axis['data']
        y_axis_label = self.y_axis['label']
        
        x_axis_data = x_axis_data[0: len(y_axis_data)]
        
        self.counts_vs_index.clear()
        self.counts_vs_index.plot(x_axis_data, y_axis_data)
        
        self.counts_vs_index.setLabel('bottom', x_axis_label)
        self.counts_vs_index.setLabel('left', y_axis_label)

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

    def done_button_clicked(self):
        self.close()

    def closeEvent(self, event=None):
        pass
