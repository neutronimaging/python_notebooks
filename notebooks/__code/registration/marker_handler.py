import pyqtgraph as pg

from __code.registration.marker_default_settings import MarkerDefaultSettings
from __code.registration.get import Get


class MarkerHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_markers(self, all=False):
        if self.parent.registration_markers_ui is None:
            return

        if all is False:
            _current_tab = self.parent.registration_markers_ui.ui.tabWidget.currentIndex()
            _tab_title = self.parent.registration_markers_ui.ui.tabWidget.tabText(_current_tab)
            self.display_markers_of_tab(marker_name=_tab_title)
        else:
            for _index, _marker_name in enumerate(self.parent.markers_table.keys()):
                self.display_markers_of_tab(marker_name=_marker_name)

    def close_all_markers(self):
        for marker in self.parent.markers_table.keys():
            self.close_markers_of_tab(marker_name=marker)

    def close_markers_of_tab(self, marker_name=''):
        """remove box and label (if they are there) of each marker"""
        _data = self.parent.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.parent.ui.image_view.removeItem(_marker_ui)

            _label_ui = _data[_file]['label_ui']
            if _label_ui:
                self.parent.ui.image_view.removeItem(_label_ui)

    def display_markers_of_tab(self, marker_name=''):
        self.close_markers_of_tab(marker_name=marker_name)
        # get short name of file selected
        o_get = Get(parent=self.parent)
        list_short_file_selected = o_get.list_short_file_selected()
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = o_get.list_row_selected()
        _color_marker = self.parent.markers_table[marker_name]['color']['name']

        pen = self.parent.markers_table[marker_name]['color']['qpen']
        for _index, _file in enumerate(list_short_file_selected):
            _marker_data = self.parent.markers_table[marker_name]['data'][_file]

            x = _marker_data['x']
            y = _marker_data['y']
            width = MarkerDefaultSettings.width
            height = MarkerDefaultSettings.height

            _marker_ui = pg.RectROI([x,y], [width, height], pen=pen)
            self.parent.ui.image_view.addItem(_marker_ui)
            _marker_ui.removeHandle(0)
            _marker_ui.sigRegionChanged.connect(self.marker_has_been_moved)

            if nbr_file_selected > 1: # more than 1 file selected, we need to add the index of the file
                text_ui = self.parent.add_marker_label(file_index=list_row_selected[_index],
                                                marker_index=marker_name,
                                                x=x,
                                                y=y,
                                                color=_color_marker)
                self.parent.markers_table[marker_name]['data'][_file]['label_ui'] = text_ui

            _marker_data['marker_ui'] = _marker_ui

    def marker_has_been_moved(self):

        o_get = Get(parent=self.parent)
        list_short_file_selected = o_get.list_short_file_selected()
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = o_get.list_row_selected()

        for _index_marker, _marker_name in enumerate(self.parent.markers_table.keys()):
            _color_marker = self.parent.markers_table[_marker_name]['color']['name']
            for _index_file, _file in enumerate(list_short_file_selected):
                _marker_data = self.parent.markers_table[_marker_name]['data'][_file]
                marker_ui = _marker_data['marker_ui']

                region = marker_ui.getArraySlice(self.parent.live_image,
                                                 self.parent.ui.image_view.imageItem)

                x0 = region[0][0].start
                y0 = region[0][1].start

                self.parent.markers_table[_marker_name]['data'][_file]['x'] = x0
                self.parent.markers_table[_marker_name]['data'][_file]['y'] = y0

                self.parent.registration_markers_ui.update_markers_table_entry(marker_name=_marker_name,
                                                                               file=_file)

                if nbr_file_selected > 1:
                    _label_ui = _marker_data['label_ui']
                    self.parent.ui.image_view.removeItem(_label_ui)
                    _label_ui = self.add_marker_label(file_index=list_row_selected[_index_file],
                                                      marker_index=_index_marker,
                                                      x=x0,
                                                      y=y0,
                                                      color=_color_marker)
                    self.parent.ui.image_view.addItem(_label_ui)
                    self.parent.markers_table[_marker_name]['data'][_file]['label_ui'] = _label_ui

    def add_marker_label(self, file_index=0, marker_index=1, x=0, y=0, color='white'):
        html_color = MarkerDefaultSettings.color_html[color]
        html_text = '<div style="text-align: center">Marker#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(int(marker_index)+1)
        html_text += '</span> - File#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(file_index)
        html_text += '</span>'
        text_ui = pg.TextItem(html=html_text, angle=45, border='w')
        self.parent.ui.image_view.addItem(text_ui)
        text_ui.setPos(x + MarkerDefaultSettings.width, y)
        return text_ui
