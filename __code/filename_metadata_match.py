import ipywe.fileselector


class FilenameMetadataMatch(object):

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_input_folder(self):
        _instruction = "Select Input Folder ..."
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instuction=_instruction,
                                                                    start_dir=self.working_dir,
                                                                    type='directory')
        self.input_folder_ui.show()

    def select_metadata_file(self):
        _instruction = "Select Metadata File ..."
        self.metadata_ui = ipywe.fileselector.FileSelectorPanel(instruction=_instruction,
                                                                start_dir=self.working_dir)
        self.metadata_ui.show()


