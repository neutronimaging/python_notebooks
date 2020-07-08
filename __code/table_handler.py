import numpy as np
from qtpy import QtGui

class TableHandler:

	def __init__(self, table_ui=None):
		self.table_ui = table_ui

	def remove_all_rows(self):
		nbr_row = self.table_ui.rowCount()
		for _ in np.arange(nbr_row):
			self.table_ui.removeRow(0)

	def set_column_names(self, column_names=None):
		self.table_ui.setHorizontalHeaderLabels(column_names)

	def set_column_sizes(self, column_sizes=None):
		for _col, _size in enumerate(column_sizes):
			self.table_ui.setColumnWidth(_col, _size)

	def insert_row(self, row=0, list_col_name=None):
		"""row is the row number
		*wargs are the contain of each column
		"""
		self.table_ui.insertRow(row)
		for column, _text in enumerate(list_col_name):
			_item = QtGui.QTableWidgetItem(_text)
			self.table_ui.setItem(row, column, _item)

	def insert_column(self, row):
		self.table_ui.insertColumn(row)
