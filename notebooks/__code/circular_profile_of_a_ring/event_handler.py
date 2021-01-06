from qtpy import QtGui


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def list_images_right_click(self):
        menu = QtGui.QMenu(self.parent)
        display_selected_radiographs = menu.addAction("Display first radiograph selected")
        menu.addSeparator()
        unselect_all = menu.addAction("Unselect all")
        action = menu.exec_(QtGui.QCursor.pos())

        if action == display_selected_radiographs:
            self.display_radiograph_of_this_row()
        elif action == unselect_all:
            self.unselect_all()

    def display_radiograph_of_this_row(self):
        pass

    def unselect_all(self):
        self.parent.ui.profile_list_images.clearSelection()
