from __code.ipywe import myfileselector as myfileselector
from __code.ipywe import fileselector as fileselector


class FileFolderBrowser(object):

    def __init__(self, working_dir='',
                 next_function=None,
                 ipts_folder=None):
        self.working_dir = working_dir
        self.next_function = next_function
        self.ipts_folder = ipts_folder

    def select_images(self, instruction='Select Images ...',
                      multiple_flag=True,
                      filters={"All": "*.*"},
                      default_filter="All"):
        self.list_images_ui = myfileselector.MyFileSelectorPanel(instruction=instruction,
                                                               start_dir=self.working_dir,
                                                               multiple=multiple_flag,
                                                               filters=filters,
                                                               default_filter=default_filter,
                                                               next=self.next_function)
        self.list_images_ui.show()

    def select_images_with_search(self, instruction='Select Images ...',
                                  multiple_flag=True,
                                  filters={"All": "*.*"},
                                  default_filter="All"):
        self.list_images_ui = fileselector.FileSelectorPanel(instruction=instruction,
                                                             start_dir=self.working_dir,
                                                             multiple=multiple_flag,
                                                             filters=filters,
                                                             default_filter=default_filter,
                                                             next=self.next_function)
        self.list_images_ui.show()

    def select_input_folder(self, instruction='Select Input Folder ...', multiple_flag=False):
        self.list_input_folders_ui = myfileselector.MyFileSelectorPanel(instruction=instruction,
                                                                        start_dir=self.working_dir,
                                                                        type='directory',
                                                                        multiple=multiple_flag,
                                                                        next=self.next_function)
        self.list_input_folders_ui.show()

    def select_output_folder(self, instruction='Select Output Folder ...', multiple_flag=False):
        self.list_output_folders_ui = myfileselector.MyFileSelectorPanel(instruction=instruction,
                                                                         start_dir=self.working_dir,
                                                                         type='directory',
                                                                         multiple=multiple_flag,
                                                                         next=self.next_function)
        self.list_output_folders_ui.show()

    def select_output_folder_with_new(self, instruction='Select Output Folder ...'):
        self.list_output_folders_ui = myfileselector.FileSelectorPanelWithJumpFolders(instruction=instruction,
                                                                                      start_dir=self.working_dir,
                                                                                      type='directory',
                                                                                      ipts_folder=self.ipts_folder,
                                                                                      next=self.next_function,
                                                                                      newdir_toolbar_button=True)
