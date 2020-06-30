class GuiUtility:

	def __init__(self, parent=None):
		self.parent = parent

	def get_tab_selected(self):
		tab_index = self.parent.ui.tabWidget.currentIndex()
		return self.parent.ui.tabWidget.tabText(tab_index)
