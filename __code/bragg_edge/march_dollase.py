from __code.table_handler import TableHandler


class MarchDollase:

	def __init__(self, parent=None):
		self.parent = parent
		self.table_ui = self.parent.ui.march_dollase_user_input_table

	def table_clicked(self, row=None, column=None):
		nbr_row = self.table_ui.rowCount()

		enabled_up_button = True
		enabled_down_button = True

		if row == 0:
			enabled_up_button = False
		if row == (nbr_row - 1):
			enabled_down_button = False

		self.parent.ui.march_dollase_user_input_up.setEnabled(enabled_up_button)
		self.parent.ui.march_dollase_user_input_down.setEnabled(enabled_down_button)

	def get_row_selected(self):
		o_table = TableHandler(table_ui=self.parent.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		return row_selected

	def move_row_up(self):
		row_selected = self.get_row_selected()
		print(f"row_selected {row_selected}")

	def move_row_down(self):
		row_selected = self.get_row_selected()
		print(f"row_selected {row_selected}")
