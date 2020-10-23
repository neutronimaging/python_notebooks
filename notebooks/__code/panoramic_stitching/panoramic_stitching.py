from IPython.core.display import display
from qtpy.QtWidgets import QMainWindow
import os

from __code.ipywe import fileselector
from __code._utilities.folder import get_list_of_folders_with_specified_file_type
from __code._utilities.string import format_html_message
from __code import load_ui


class PanoramicStitching:

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.file_extension = ["tiff", "tif"]

    def select_input_folders(self):
        self.list_folder_widget = fileselector.FileSelectorPanel(instruction='select all the folders of images to '
                                                                             'stitch',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.folder_selected,
                                                                 multiple=True)
        self.list_folder_widget.show()

    def folder_selected(self, folder_selected):
        final_list_folders = get_list_of_folders_with_specified_file_type(list_of_folders_to_check=folder_selected,
                                                                          file_extension=self.file_extension)
        if not final_list_folders:

            str_list_ext = ", ".join(self.file_extension)
            display(format_html_message(pre_message="None of the folder selected contains the file of extension "
                                                    "requested ({}}".format(str_list_ext),
                                        spacer=""))
            return

        final_list_folders.sort()
        nbr_folder = len(final_list_folders)
        display(format_html_message(pre_message="Notebook is about to work with {} folders!".format(nbr_folder),
                                    spacer=""))

        o_interface = Interface(working_dir=self.working_dir, list_folders=final_list_folders)


class Interface(QMainWindow):

    def __init__(self, parent=None, working_dir=None, list_folders=None):
        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))
        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_panoramic_stitching_manual.ui'))
        print(ui_full_path)
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Panoramic Stitching")

