from qtpy.QtWidgets import QDialog
from qtpy.QtGui import QPixmap
import os
from __code import load_ui


class RegistrationAutoConfirmationLauncher:

    parent = None

    def __init__(self, parent=None):
        self.parent=parent

        if self.parent.registration_auto_confirmation_ui is None:
            conf_ui = RegistrationManualAutoConfirmation(parent=parent)
            conf_ui.show()
            self.parent.registration_auto_confirmation_ui = conf_ui
        else:
            self.parent.registration_auto_confirmation_ui.setFocus()
            self.parent.registration_auto_confirmation_ui.activateWindow()


class RegistrationManualAutoConfirmation(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_registration_auto_confirmation.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.initialize_widgets()

    def initialize_widgets(self):
        _file_path = os.path.dirname(__file__)
        warning_image_file = os.path.abspath(os.path.join(_file_path, '../static/warning_icon.png'))
        warning_image = QPixmap(warning_image_file)
        self.ui.warning_label.setPixmap(warning_image)

    def yes_button_clicked(self):
        self.parent.registration_auto_confirmation_ui.close()
        self.parent.registration_auto_confirmation_ui = None
        self.parent.start_auto_registration()

    def no_button_clicked(self):
        self.closeEvent()

    def closeEvent(self, event=None):
        self.parent.registration_auto_confirmation_ui.close()
        self.parent.registration_auto_confirmation_ui = None
