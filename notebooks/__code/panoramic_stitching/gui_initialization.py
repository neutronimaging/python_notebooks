import os
import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QProgressBar
from qtpy.QtGui import QIcon
from qtpy.QtCore import QSize
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.table_handler import TableHandler


class GuiInitialization:

    button = {'left': {'pressed': 'left_arrow_v2_pressed.png',
                       'released': 'left_arrow_v2_released.png'},
              'right': {'pressed': 'right_arrow_v2_pressed.png',
                        'released': 'right_arrow_v2_released.png'},
              'left_left': {'pressed': 'left_left_arrow_v2_pressed.png',
                            'released': 'left_left_arrow_v2_released.png'},
              'right_right': {'pressed': 'right_right_arrow_v2_pressed.png',
                              'released': 'right_right_arrow_v2_released.png'},
              'up': {'pressed': 'up_arrow_v2_pressed.png',
                     'released': 'up_arrow_v2_released.png'},
              'down': {'pressed': 'down_arrow_v2_pressed.png',
                       'released': 'down_arrow_v2_released.png'},
              'up_up': {'pressed': 'up_up_arrow_v2_pressed.png',
                        'released': 'up_up_arrow_v2_released.png'},
              'down_down': {'pressed': 'down_down_arrow_v2_pressed.png',
                            'released': 'down_down_arrow_v2_released.png'},
              }

    button_size = {'single_arrow': {'width': 50,
                                             'height': 50},
                   'double_arrow': {'width': 65,
                                             'height': 50},
                   'single_vertical_arrow': {'width': 50,
                                             'height': 50},
                   'double_vertical_arrow': {'width': 50,
                                             'height': 65},
                   }

    def __init__(self, parent=None):
        self.parent = parent

    def before_loading_data(self):
        self.block_signals(True)
        self.statusbar()
        self.splitter()
        self.pyqtgraph()
        self.matplotlib()
        self.widgets()
        self.table()
        self.block_signals(False)

    def block_signals(self, status):
        list_ui = [self.parent.ui.list_folders_combobox,
                   self.parent.ui.tableWidget]
        for _ui in list_ui:
            _ui.blockSignals(status)

    def splitter(self):
        self.parent.ui.profile_display_splitter.setSizes([500, 500])
        self.parent.ui.display_splitter.setSizes([200, 100])
        self.parent.ui.full_splitter.setSizes([400, 100])

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.stitched_widget.setLayout(image_layout)

    def matplotlib(self):
        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=4, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.horizontal_profile_plot = _matplotlib(parent=self.parent,
                                                          widget=self.parent.ui.horizontal_profile_plot_widget)
        self.parent.kropff_low_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.vertical_profile_plot_widget)

    def widgets(self):
        # list_folders
        list_folders = self.parent.list_folders
        self.parent.ui.list_folders_combobox.addItems(list_folders)
        # hide error label
        self.parent.ui.from_to_error_label.setVisible(False)
        # move buttons
        _file_path = os.path.dirname(__file__)

        up_up_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['up_up']
                                                                                                  ['released'])
        self.parent.ui.up_up_button.setIcon(QIcon(up_up_arrow_file))
        up_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['up']
                                                                                               ['released'])
        self.parent.ui.up_button.setIcon(QIcon(up_arrow_file))
        left_left_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button[
                                                                                               'left_left']
                                                                                              ['released'])
        self.parent.ui.left_left_button.setIcon(QIcon(left_left_arrow_file))
        left_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['left']
                                                                                      ['released'])
        self.parent.ui.left_button.setIcon(QIcon(left_arrow_file))
        right_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['right']
                                                                                       ['released'])
        self.parent.ui.right_button.setIcon(QIcon(right_arrow_file))
        right_right_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['right_right']
                                                                                       ['released'])
        self.parent.ui.right_right_button.setIcon(QIcon(right_right_arrow_file))

        down_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button['down']
                                                                                                  ['released'])
        self.parent.ui.down_button.setIcon(QIcon(down_arrow_file))
        down_down_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(self.button[
                                                                                               'down_down']
                                                                                                  ['released'])
        self.parent.ui.down_down_button.setIcon(QIcon(down_down_arrow_file))

        list_ui = [self.parent.ui.left_button,
                   self.parent.ui.right_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=self.button_size['single_arrow']['width'],
                                             height=self.button_size['single_arrow']['height'])

        list_ui = [self.parent.ui.left_left_button,
                   self.parent.ui.right_right_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=self.button_size['double_arrow']['width'],
                                             height=self.button_size['double_arrow']['height'])

        list_ui = [self.parent.ui.up_button,
                   self.parent.ui.down_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=self.button_size['single_vertical_arrow']['width'],
                                             height=self.button_size['single_vertical_arrow']['height'])

        list_ui = [self.parent.ui.up_up_button,
                   self.parent.ui.down_down_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=self.button_size['double_vertical_arrow']['width'],
                                             height=self.button_size['double_vertical_arrow']['height'])



    def table(self):
        column_sizes = [900, 100, 100, 100]
        column_names = ['File name', 'xoffset (px)', 'yoffset (px)', 'visible?']
        o_table = TableHandler(table_ui=self.parent.tableWidget)
        o_table.set_column_sizes(column_sizes=column_sizes)
        o_table.set_column_names(column_names=column_names)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def after_loading_data(self):
        self.parent.list_folder_combobox_value_changed()
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.select_rows(list_of_rows=[1])

    @staticmethod
    def __make_full_file_name_to_static_folder_of(file_name):
        _file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        full_path_file = os.path.abspath(os.path.join(_file_path, file_name))
        return full_path_file

    @staticmethod
    def __set_widgets_size(widgets=[], width=10, height=10):
        for _widget in widgets:
            _widget.setIconSize(QSize(width, height))
