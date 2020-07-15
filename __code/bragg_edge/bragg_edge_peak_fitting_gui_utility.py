class GuiUtility:

	def __init__(self, parent=None):
		self.parent = parent

	def get_tab_selected(self, tab_ui=None):
		tab_index = tab_ui.currentIndex()
		return tab_ui.tabText(tab_index)

	def get_toolbox_selected(self, toolbox_ui=None):
		toolbox_index = toolbox_ui.currentIndex()
		return toolbox_ui.itemText(toolbox_index)
