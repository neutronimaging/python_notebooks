from __code.file_folder_browser import FileFolderBrowser


class SelectFiles(FileFolderBrowser):

    list_of_files = []

    def __init__(self, system=None):
        working_dir = system.System.get_working_dir()

        super(SelectFiles, self).__init__(working_dir=working_dir,
                                          next_function=self.retrieve_list_of_files)

        filters = {"TIFF": "*.tif"}
        default_filter = "TIFF"
        self.select_images(filters=filters,
                           default_filter=default_filter)

    def retrieve_list_of_files(self, list_of_files=''):
        self.list_of_files = list_of_files


class SelectFolder(FileFolderBrowser):

    def __init__(self, system=None, next_function=None):
        working_dir = system.System.get_working_dir()

        super(SelectFolder, self).__init__(working_dir=working_dir,
                                           next_function=next_function)

        self.select_output_folder()
