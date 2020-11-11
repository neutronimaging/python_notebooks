import os
import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout, QProgressBar
from qtpy.QtGui import QIcon
import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.utilities import make_full_file_name_to_static_folder_of, set_widgets_size
from __code.panoramic_stitching.config_buttons import button
from __code.panoramic_stitching.gui_handler import GuiHandler


class GuiInitialization:
    button_size = {'single_arrow'         : {'width' : 50,
                                             'height': 50},
                   'double_arrow'         : {'width' : 65,
                                             'height': 50},
                   'single_vertical_arrow': {'width' : 50,
                                             'height': 50},
                   'double_vertical_arrow': {'width' : 50,
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
        self.tab()
        self.block_signals(False)

    def tab(self):
        self.parent.ui.top_tabWidget.setTabEnabled(1, False)

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
        # calculate best contrast images
        _view1 = pg.PlotItem()
        self.parent.ui.image_view_best_contrast = pg.ImageView(view=_view1, name='view1')
        self.parent.ui.image_view_best_contrast.ui.roiBtn.hide()
        self.parent.ui.image_view_best_contrast.ui.menuBtn.hide()
        image_layout_best_contrast = QVBoxLayout()
        image_layout_best_contrast.addWidget(self.parent.ui.image_view_best_contrast)
        self.parent.ui.best_contrast_widget.setLayout(image_layout_best_contrast)

        # stitch images
        _view2 = pg.PlotItem()
        self.parent.ui.image_view = pg.ImageView(view=_view2, name='view2')
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
        self.parent.vertical_profile_plot = _matplotlib(parent=self.parent,
                                                        widget=self.parent.ui.vertical_profile_plot_widget)

    def widgets(self):
        # list_folders
        list_folders = self.parent.list_folders
        self.parent.ui.list_folders_combobox.addItems(list_folders)

        # hide error label
        self.parent.ui.from_to_error_label.setVisible(False)

        # move buttons
        _file_path = os.path.dirname(__file__)

        up_up_arrow_file = make_full_file_name_to_static_folder_of(button['up_up']
                                                                   ['released'])
        self.parent.ui.up_up_button.setIcon(QIcon(up_up_arrow_file))
        up_arrow_file = make_full_file_name_to_static_folder_of(button['up']
                                                                ['released'])
        self.parent.ui.up_button.setIcon(QIcon(up_arrow_file))
        left_left_arrow_file = make_full_file_name_to_static_folder_of(button[
                                                                           'left_left']
                                                                       ['released'])
        self.parent.ui.left_left_button.setIcon(QIcon(left_left_arrow_file))
        left_arrow_file = make_full_file_name_to_static_folder_of(button['left']
                                                                  ['released'])
        self.parent.ui.left_button.setIcon(QIcon(left_arrow_file))
        right_arrow_file = make_full_file_name_to_static_folder_of(button['right']
                                                                   ['released'])
        self.parent.ui.right_button.setIcon(QIcon(right_arrow_file))
        right_right_arrow_file = make_full_file_name_to_static_folder_of(button['right_right']
                                                                         ['released'])
        self.parent.ui.right_right_button.setIcon(QIcon(right_right_arrow_file))

        down_arrow_file = make_full_file_name_to_static_folder_of(button['down']
                                                                  ['released'])
        self.parent.ui.down_button.setIcon(QIcon(down_arrow_file))
        down_down_arrow_file = make_full_file_name_to_static_folder_of(button[
                                                                           'down_down']
                                                                       ['released'])
        self.parent.ui.down_down_button.setIcon(QIcon(down_down_arrow_file))

        list_ui = [self.parent.ui.left_button,
                   self.parent.ui.right_button]
        set_widgets_size(widgets=list_ui,
                         width=self.button_size['single_arrow']['width'],
                         height=self.button_size['single_arrow']['height'])

        list_ui = [self.parent.ui.left_left_button,
                   self.parent.ui.right_right_button]
        set_widgets_size(widgets=list_ui,
                         width=self.button_size['double_arrow']['width'],
                         height=self.button_size['double_arrow']['height'])

        list_ui = [self.parent.ui.up_button,
                   self.parent.ui.down_button]
        set_widgets_size(widgets=list_ui,
                         width=self.button_size['single_vertical_arrow']['width'],
                         height=self.button_size['single_vertical_arrow']['height'])

        list_ui = [self.parent.ui.up_up_button,
                   self.parent.ui.down_down_button]
        set_widgets_size(widgets=list_ui,
                         width=self.button_size['double_vertical_arrow']['width'],
                         height=self.button_size['double_vertical_arrow']['height'])

        state_hori_matplotlib = self.parent.ui.enable_horizontal_profile_checkbox.isChecked()
        o_gui = GuiHandler(parent=self.parent)
        o_gui.enabled_horizontal_profile_widgets(enabled=state_hori_matplotlib)

        state_verti_matplotlib = self.parent.ui.enable_vertical_profile_checkbox.isChecked()
        o_gui.enabled_vertical_profile_widgets(enabled=state_verti_matplotlib)

        profile_sliders = [self.parent.ui.horizontal_profile_width_slider,
                           self.parent.ui.vertical_profile_width_slider]
        for _slider in profile_sliders:
            _slider.setMinimum(self.parent.width_profile['min'])
            _slider.setMaximum(self.parent.width_profile['max'])
            _slider.setValue(self.parent.width_profile['default'])

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
        self.parent.best_contrast_list_folders_combobox_changed()

        # bin size of best contrast (nbr of images / 100 by default)
        bin_size = np.int(self.parent.nbr_files_per_folder / self.parent.default_best_contrast_bin_size_divider)
        self.parent.ui.best_contrast_bin_size_value.setText(str(bin_size))

        # self.parent.list_folder_combobox_value_changed()
        # o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        # o_table.select_rows(list_of_rows=[1])
