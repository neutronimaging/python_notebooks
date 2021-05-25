from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QApplication


class StatusMessageStatus:

    ready = "QStatusBar{padding-left:8px;background:rgba(236,236,236,75);color:green;font-weight:normal;}"
    working = "QStatusBar{padding-left:8px;background:rgba(105,105,105,75);color:rgb(210,105,30);font-weight:normal;}"
    error = "QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}"
    warning = "QStatusBar{padding-left:8px;background:rgba(236,236,236,75);color:red;font-weight:normal;}"


def show_status_message(parent=None, message="", status=StatusMessageStatus.ready, duration_s=None):
    parent.ui.statusbar.setStyleSheet(status)
    if duration_s:
        parent.ui.statusbar.showMessage(message, duration_s * 1000)
    else:
        parent.ui.statusbar.showMessage(message)
    QGuiApplication.processEvents()
    parent.ui.repaint()
    QApplication.processEvents()
