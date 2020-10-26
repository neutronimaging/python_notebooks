class ComboboxHandler:

    def __init__(self, combobox_ui=None):
        self.combobox_ui = combobox_ui

    def clear(self):
        self.combobox_ui.clear()

    def add_items(self, list_string=None):
        self.combobox_ui.addItems(list_string)
