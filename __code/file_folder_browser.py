import ipywe.fileselector


class FileFolderBrowser(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_images(self, instruction='Select Images ...', multiple_flag=True):
        self.list_images_ui = ipywe.fileselector.FileSelectorPanel(instruction=instruction,
                                                                   start_dir=self.working_dir,
                                                                   multiple=multiple_flag)
        self.list_images_ui.show()

    def select_input_folder(self, instruction='Select Input Folder ...', multiple_flag=False):
        self.list_input_folders_ui = ipywe.fileselector.FileSelectorPanel(instruction=instruction,
                                                                          start_dir=self.working_dir,
                                                                          type='directory',
                                                                          multiple=multiple_flag)
        self.list_input_folders_ui.show()

    def select_output_folder(self, instruction='Select Output Folder ...', multiple_flag=False):
        self.list_output_folders_ui = ipywe.fileselector.FileSelectorPanel(instruction=instruction,
                                                                           start_dir=self.working_dir,
                                                                           type='directory',
                                                                           multiple=multiple_flag)
        self.list_output_folders_ui.show()
