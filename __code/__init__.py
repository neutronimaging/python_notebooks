from qtpy.uic import loadUi

__all__ = ['load_ui']
__version__ = "1.0.0"

def load_ui(ui_filename, baseinstance):
    return loadUi(ui_filename, baseinstance=baseinstance)
