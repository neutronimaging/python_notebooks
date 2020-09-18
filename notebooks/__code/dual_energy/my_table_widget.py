from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import QTableWidget, QWidget, QVBoxLayout, QApplication


class MyTableWidget(QTableWidget):

	def __init__(self, parent=None):
		self.parent = parent
		QTableWidget.__init__(self)
		self.keys = [Qt.Key_Left,
					 Qt.Key_Right]

		# We need this to allow navigating without editing
		self.catch = False

	def focusInEvent(self, event):
		self.catch = False
		return QTableWidget.focusInEvent(self, event)

	def focusOutEvent(self, event):
		self.catch = True
		return QTableWidget.focusOutEvent(self, event)

	def event(self, event):
		if self.catch and event.type() == QEvent.KeyRelease and event.key() in self.keys:
			self._moveCursor(event.key())
		return QTableWidget.event(self, event)

	def keyPressEvent(self, event):
		self._moveCursor(event.key())
		# if not self.catch:
		# 	return QTableWidget.keyPressEvent(self, event)

	def _moveCursor(self, key):
		row = self.currentRow()
		col = self.currentColumn()

		prev_row = row
		prev_col = col

		if key == Qt.Key_Left and col > 0:
			col -= 1
		elif key == Qt.Key_Right and col < (self.columnCount()-1):
			col += 1
		elif key == Qt.Key_Up and row > 0:
			row -= 1
		elif key == Qt.Key_Down and row < (self.rowCount()-1):
			row += 1
		else:
			return
		try:
			self.setCurrentCell(row, col)
			self.parent.calculation_table_cell_clicked(row, col)
		except IndexError:
			self.setCurrentCell(prev_row, prev_col)
