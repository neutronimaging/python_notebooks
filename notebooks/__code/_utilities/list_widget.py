class ListWidget:

    def __init__(self, ui=None):
        self.ui = ui

    def get_current_row(self):
        return self.ui.currentRow()

    def set_current_row(self, row=0):
        self.ui.setCurrentRow(row)

    def get_number_elements(self):
        return self.ui.count()

    def select_next_element(self):
        current_row = self.get_current_row()
        self.ui.setCurrentRow(current_row+1)

    def select_previous_element(self):
        current_row = self.get_current_row()
        self.ui.setCurrentRow(current_row-1)

    def select_element(self, row=0):
        self.ui.setCurrentRow(row)
