class WidgetsHandler:

    @staticmethod
    def block_signals(ui=None, status=True):
        if ui is None:
            return

        ui.blockSignals(status)
