import numpy as np
from qtpy import QtGui
import pyqtgraph as pg

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.get import Get

COLOR_LOCK = QtGui.QColor(62, 13, 244, 100)
COLOR_UNLOCK = QtGui.QColor(255, 0, 0, 100)
COLOR_LINE_SEGMENT = QtGui.QColor(255, 0, 255)
LINE_SEGMENT_FONT = QtGui.QFont("Arial", 15)

ROI_WIDTH, ROI_HEIGHT = 50, 50


class ImageHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def update_contour_plot(self):
        if self.parent.contour_image_roi_id:
            self.parent.ui.image_view.removeItem(self.parent.contour_image_roi_id)

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        name_of_file_selected = o_table.get_item_str_from_cell(row=row_selected, column=0)

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        roi = {'x0': offset_dictionary[name_of_file_selected]['xoffset'],
               'y0': offset_dictionary[name_of_file_selected]['yoffset']}

        if row_selected == 0:
            _color = COLOR_LOCK
        else:
            _color = COLOR_UNLOCK

        if roi:
            _pen = QtGui.QPen()
            _pen.setColor(_color)
            _pen.setWidthF(0.01)
            _roi_id = pg.ROI([roi['x0'], roi['y0']],
                             [self.parent.image_width, self.parent.image_height],
                             pen=_pen, scaleSnap=True,
                             movable=False)
            self.parent.ui.image_view.addItem(_roi_id)
            self.parent.contour_image_roi_id = _roi_id

    def update_current_panoramic_image(self):

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()

        data_dictionary = self.parent.data_dictionary[folder_selected]
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        max_yoffset, max_xoffset = self.get_max_offset(folder_selected=folder_selected)

        image_height = self.parent.image_height
        image_width = self.parent.image_width

        _color = None

        panoramic_image = None
        for _file_index, _file in enumerate(data_dictionary.keys()):

            if _file_index == 0:
                panoramic_image = np.zeros((max_yoffset + image_height, max_xoffset + image_width))

            _image = data_dictionary[_file].data
            is_visible = offset_dictionary[_file]['visible']
            if not is_visible:
                continue

            if _file_index == 0:
                panoramic_image[0:image_height, 0:image_width] = _image
            else:
                xoffset = offset_dictionary[_file]['xoffset']
                yoffset = offset_dictionary[_file]['yoffset']

                panoramic_image[yoffset: yoffset+image_height, xoffset: xoffset+image_width] = _image

        self.parent.panoramic_images[folder_selected] = panoramic_image

        _image = np.transpose(panoramic_image)
        # _image = self._clean_image(_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.current_live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0],
                                    self.parent.histogram_level[1])

    def get_max_offset(self, folder_selected=None):
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        list_xoffset = [offset_dictionary[_key]['xoffset'] for _key in offset_dictionary.keys()]
        list_yoffset = [offset_dictionary[_key]['yoffset'] for _key in offset_dictionary.keys()]

        return np.int(np.max(list_yoffset)), np.int(np.max(list_xoffset))

    def update_from_to_roi(self, state=False):

        if self.parent.from_roi_id:
            self.parent.ui.image_view.removeItem(self.parent.from_roi_id)
            self.parent.ui.image_view.removeItem(self.parent.to_roi_id)
            self.parent.ui.image_view.removeItem(self.parent.from_label_id)
            self.parent.ui.image_view.removeItem(self.parent.to_label_id)
            self.parent.ui.image_view.removeItem(self.parent.from_roi_cross_id)
            self.parent.ui.image_view.removeItem(self.parent.to_roi_cross_id)

        if state:

            from_roi = self.parent.from_roi
            x = from_roi['x']
            y = from_roi['y']
            self.parent.from_roi_id = pg.ROI([x, y],
                                             [ROI_WIDTH, ROI_HEIGHT],
                                             scaleSnap=True)
            self.parent.ui.image_view.addItem(self.parent.from_roi_id)
            self.parent.from_roi_id.sigRegionChanged.connect(self.parent.from_roi_box_changed)

            to_roi = self.parent.to_roi
            x = to_roi['x']
            y = to_roi['y']
            self.parent.to_roi_id = pg.ROI([x, y],
                                           [ROI_WIDTH, ROI_HEIGHT],
                                           scaleSnap=True)
            self.parent.ui.image_view.addItem(self.parent.to_roi_id)
            self.parent.to_roi_id.sigRegionChanged.connect(self.parent.to_roi_box_changed)

            self.update_from_label()
            self.update_from_cross_line()
            self.update_to_label()
            self.update_to_cross_line()

    def update_from_to_line_label_changed(self):
        from_to_roi = self.parent.from_to_roi
        x0 = from_to_roi['x0']
        y0 = from_to_roi['y0']
        x1 = from_to_roi['x1']
        y1 = from_to_roi['y1']

        self.parent.from_label_id.setPos(x1, y1)
        self.parent.to_label_id.setPos(x0, y0)

    def update_cross_line(self, roi_cross_id=None, roi=None):
        if roi_cross_id:
            self.parent.ui.image_view.removeItem(roi_cross_id)

        pos = []
        adj = []

        x = roi['x']
        y = roi['y']

        # vertical guide
        pos.append([x + ROI_WIDTH / 2, y - ROI_HEIGHT / 2])
        pos.append([x + ROI_WIDTH / 2, y + ROI_HEIGHT + ROI_HEIGHT / 2])
        adj.append([0, 1])

        # horizontal guide
        pos.append([x - ROI_WIDTH / 2, y + ROI_HEIGHT / 2])
        pos.append([x + ROI_WIDTH + ROI_WIDTH / 2, y + ROI_HEIGHT / 2])
        adj.append([2, 3])

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = (255, 0, 0, 255, 1)
        lines = np.array([line_color for _ in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])
        line_view_binning = pg.GraphItem()
        self.parent.ui.image_view.addItem(line_view_binning)
        line_view_binning.setData(pos=pos,
                                  adj=adj,
                                  pen=lines,
                                  symbol=None,
                                  pxMode=False)

        return line_view_binning

    def update_from_cross_line(self):
        from_roi_cross_id = self.parent.from_roi_cross_id
        from_roi = self.parent.from_roi

        self.parent.from_roi_cross_id = self.update_cross_line(roi_cross_id=from_roi_cross_id,
                                                               roi=from_roi)

    def update_to_cross_line(self):
        to_roi_cross_id = self.parent.to_roi_cross_id
        to_roi = self.parent.to_roi

        self.parent.to_roi_cross_id = self.update_cross_line(roi_cross_id=to_roi_cross_id,
                                                             roi=to_roi)

    def update_label(self, label_id=None, roi=None, text=""):
        if label_id:
            self.parent.ui.image_view.removeItem(label_id)

        x = roi['x'] + ROI_WIDTH
        y = roi['y']

        _text_id = pg.TextItem(text=text)
        _text_id.setPos(x, y)
        _text_id.setFont(LINE_SEGMENT_FONT)
        self.parent.ui.image_view.addItem(_text_id)

        return _text_id

    def update_from_label(self):
        label_id = self.parent.from_label_id
        roi = self.parent.from_roi
        self.parent.from_label_id = self.update_label(label_id=label_id, roi=roi, text="from")

    def update_to_label(self):
        label_id = self.parent.to_label_id
        roi = self.parent.to_roi
        self.parent.to_label_id = self.update_label(label_id=label_id, roi=roi, text="to")
