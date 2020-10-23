from __code.ipywe import fileselector


class PanoramicStitching:

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folders(self):
        self.list_folder_widget = fileselector.FileSelectorPanel(instruction='select all the folders of images to '
                                                                             'stitch',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.folder_selected,
                                                                 multiple=True)
        self.list_folder_widget.show()

    def folder_selected(self, folder_selected):


