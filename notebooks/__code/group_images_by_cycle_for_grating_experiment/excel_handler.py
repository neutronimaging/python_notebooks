import pandas as pd
from qtpy.QtWidgets import QMainWindow
from IPython.core.display import display
import os

from __code._utilities.string import format_html_message
from __code import load_ui


class ExcelHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self, excel_file=None):
        if excel_file is None:
            return

        df = pd.read_excel(excel_file, sheet_name="Tabelle1", header=0)
        list_columns = df.columns

        self.parent.excel_info_widget.value = f"<b>Loaded excel file</b>: {excel_file}!"

        o_interface = Interface(grand_parent=self.parent)
        o_interface.show()


class Interface(QMainWindow):

    def __init__(self, parent=None, grand_parent=None):

        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_editor.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Excel Editor")
