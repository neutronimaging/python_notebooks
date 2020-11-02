class GuiHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def enabled_vertical_profile_widgets(self, enabled):
        list_verti_ui = [self.parent.ui.vertical_profile_plot_widget,
                         self.parent.ui.vertical_profile_width_slider]
        for _ui in list_verti_ui:
            _ui.setEnabled(enabled)

    def enabled_horizontal_profile_widgets(self, enabled):
        list_hori_ui = [self.parent.ui.horizontal_profile_plot_widget,
                        self.parent.ui.horizontal_profile_width_slider]
        for _ui in list_hori_ui:
            _ui.setEnabled(enabled)