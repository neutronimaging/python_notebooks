import os
from qtpy.QtWidgets import QMainWindow

from __code import load_ui


class InterfaceHandler:

    def __init__(self, working_dir=None, o_norm=None):
        o_interface = Interface(data=o_norm.data['sample'],
                                working_dir=working_dir)
        o_interface.show()


class Interface(QMainWindow):

    def __init__(self, parent=None, data=None, working_dir=None):

        self.data = data
        self.working_dir = working_dir

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_circular_profile_of_a_ring.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Circular Profile of a Ring")

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
    