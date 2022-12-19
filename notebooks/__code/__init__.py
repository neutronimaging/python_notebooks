from qtpy.uic import loadUi

LOGGER_FILE = "/SNS/users/j35/logger/notebook_logger.log"
#LOGGER_FILE = "/Users/j35/logger/notebook_logger.log"

__all__ = ['load_ui']


def load_ui(ui_filename, baseinstance):
    return loadUi(ui_filename, baseinstance=baseinstance)
