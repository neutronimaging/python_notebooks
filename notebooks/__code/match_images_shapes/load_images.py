from IPython.display import HTML, display

try:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QFileDialog, QMainWindow
except ImportError:
    pass

from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector


class LoadImages:
    nbr_files = 0
    images_dimension = {"height": 0, "width": 0}

    working_data = []
    working_dir = ""
    list_images = []

    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    def select_images(self, use_next=False):
        if use_next:
            next = self.load_images
        else:
            next = None
        display(
            HTML(
                '<span style="font-size: 20px; color:blue">Select the images you want to work on!</span>'
            )
        )
        self.list_images_ui = fileselector.FileSelectorPanel(
            instruction="Select Images...",
            multiple=True,
            next=next,
            start_dir=self.working_dir,
        )
        self.list_images_ui.show()

    def load_images(self, list_images=[]):
        if list_images == []:
            list_images = self.list_images_ui.selected

        self.o_norm = Normalization()
        self.o_norm.load(file=list_images, notebook=True, check_shape=False)

        self.nbr_files = len(list_images)
        # [self.images_dimension['height'], self.images_dimension['width']] = \
        #     np.shape(self.o_norm.data['sample']['data'][0])
        self.working_data = self.o_norm.data["sample"]["data"]
        self.list_images = list_images
        self.working_metadata = self.o_norm.data["sample"]["metadata"]
