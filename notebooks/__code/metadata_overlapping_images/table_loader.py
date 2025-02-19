import numpy as np
import pandas as pd


class TableLoader:

    table = {}

    def __init__(self, parent=None, filename=''):
        self.parent = parent
        self.filename = filename

    def load_table(self):
        table = pd.read_csv(self.filename,
                            sep=',',
                            comment='#',
                            names=["filename", "metadata"])
        table_dict = {}
        for _row in table.values:
            _key, _value = _row
            table_dict[_key] = _value

        self.table = table_dict

    def populate(self):
        """This will look at the filename value in the first column of tableWidget and if they match if any
        of the key of the dictionary, it will populate the value column"""

        # populate with new entries
        nbr_row = self.parent.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            table_key = self.parent.ui.tableWidget.item(_row, 0).text()
            value = self.table.get(table_key, "")
            self.parent.ui.tableWidget.item(_row, 1).setText(str(value))
