class GuiUtility:

	cell_str_format = "{:.3f}"

	def __init__(self, parent=None):
		self.parent = parent

	def get_tab_selected(self, tab_ui=None):
		tab_index = tab_ui.currentIndex()
		return tab_ui.tabText(tab_index)

	def get_toolbox_selected(self, toolbox_ui=None):
		toolbox_index = toolbox_ui.currentIndex()
		return toolbox_ui.itemText(toolbox_index)

	def update_kropff_high_lambda_table_ui(self, row=0, a0=None, b0=None, a0_error=None, b0_error=None):
		table_ui = self.parent.ui.high_lambda_tableWidget
		table_ui.item(row, 1).setText(self.cell_str_format.format(a0))
		table_ui.item(row, 2).setText(self.cell_str_format.format(b0))
		table_ui.item(row, 3).setText(self.cell_str_format.format(a0_error))
		table_ui.item(row, 4).setText(self.cell_str_format.format(b0_error))
