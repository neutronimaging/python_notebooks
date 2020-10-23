class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.splitter()

    def splitter(self):
        self.parent.ui.profile_display_splitter.setSizes([500, 500])
        self.parent.ui.display_splitter.setSizes([200, 100])
        self.parent.ui.full_splitter.setSizes([400, 100])
