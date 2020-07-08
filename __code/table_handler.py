import numpy as np
from qtpy import QtGui


class TableHandler:

	def __init__(self, table_ui=None):
		self.table_ui = table_ui

	def remove_all_rows(self):
		nbr_row = self.table_ui.rowCount()
		for _ in np.arange(nbr_row):
			self.table_ui.removeRow(0)

	def insert_row(self, row=0, *args):
		"""row is the row number
		*wargs are the contain of each column
		"""
		self.table_ui.insertRow(row)

		for column, _text in enumerate(*args):
			_item = QtGui.QTableWidgetItem(str(_text))
			self.table_ui.setItem(row, column, _item)
