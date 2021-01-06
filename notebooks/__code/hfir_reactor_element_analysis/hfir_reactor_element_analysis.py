from __code.ipywe import fileselector


class HfirReactorElementAnalysis:

    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    def select_ascii_file(self):
        ascii_file_ui = fileselector.FileSelectorPanel(instruction="Select ASCII file ...",
                                                       start_dir=self.working_dir,
                                                       next=self.load_ascii,
                                                       filters={"CSV": "*.csv"},
                                                       default_filter="CSV")
        ascii_file_ui.show()

    def load_ascii(self, ascii_file_name):
        print(ascii_file_name)
