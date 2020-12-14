import os
from qtpy.QtWidgets import QMainWindow
import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout
import numpy as np

from __code import load_ui


class InterfaceHandler:

    def __init__(self, working_dir=None, o_norm=None):
        o_interface = Interface(data=o_norm.data['sample']['data'],
                                working_dir=working_dir)
        o_interface.show()


class Interface(QMainWindow):

    histogram_level = None
    current_live_image = None

    def __init__(self, parent=None, data=None, working_dir=None):

        self.data = data
        self.working_dir = working_dir

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_circular_profile_of_a_ring.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Circular Profile of a Ring")

        self.init_widgets()
        self.slider_image_changed(new_index=0)

    def init_widgets(self):
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(image_layout)

        self.ui.splitter.setSizes([500, 200])

        nbr_files = len(self.data)
        self.ui.image_slider.setMaximum(nbr_files-1)

    def help_button_clicked(self):
        pass

    def guide_color_changed(self, index_position):
        pass

    def guide_color_clicked(self):
        pass

    def guide_color_released(self):
        pass

    def grid_slider_moved(self, index):
        pass

    def grid_slider_pressed(self):
        pass

    def export_profiles_clicked(self):
        pass

    def cancel_clicked(self):
        pass

    def calculate_profiles_clicked(self):
        pass

    def slider_image_changed(self, new_index=0):

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level is None:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        data = self.data[new_index]
        _image = np.transpose(data)
        self.ui.image_view.setImage(_image)
        self.current_live_image = _image

        _view_box.setState(_state)
        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0],
                                    self.histogram_level[1])
