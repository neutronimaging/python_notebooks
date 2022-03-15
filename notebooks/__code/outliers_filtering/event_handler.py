import numpy as np

from NeuNorm.normalization import Normalization

from __code._utilities.table_handler import TableHandler
from __code.outliers_filtering.display import Display
from __code.outliers_filtering.algorithm import Algorithm


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def algorithm_changed(self):
        high_intensity_status = self.parent.ui.fix_high_intensity_counts_checkBox.isChecked()
        self.parent.ui.median_thresholding_frame.setEnabled(high_intensity_status)
        self.reset_table_infos()
        self.table_selection_changed()

    def reset_table_infos(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            for _col in np.arange(1, 5):
                o_table.insert_item(row=_row,
                                    column=_col,
                                    editable=False,
                                    value="")

    def table_selection_changed(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        short_file_name = self.parent.list_short_file_name[row_selected]
        if self.parent.data.get(short_file_name, None) is None:
            self.parent.data[short_file_name] = {'raw': self.load_raw_data(row=row_selected),
                                                 'filtered': None}

        if self.parent.image_size is None:
            [height, width] = np.shape(self.parent.data[short_file_name]['raw'])
            self.parent.image_size = [height, width]

        filtered_data = self.calculate_filtered_data(raw_data=self.parent.data[short_file_name]['raw'])

        o_display = Display(parent=self.parent)
        self.parent.data[short_file_name]['filtered'] = filtered_data
        o_display.filtered_image(data=filtered_data)
        o_display.raw_image(data=self.parent.data[short_file_name]['raw'])

    def load_raw_data(self, row=0):
        file = self.parent.list_files[row]
        o_norm = Normalization()
        o_norm.load(file=file, auto_gamma_filter=False,
                    manual_gamma_filter=False)
        _raw_data = np.squeeze(o_norm.data['sample']['data'])
        return _raw_data

    def calculate_filtered_data(self, raw_data=None):

        o_algo = Algorithm(parent=self.parent,
                           data=raw_data)
        o_algo.run()

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        high_counts_stats = o_algo.get_high_counts_stats()

        o_table.insert_item(row=row_selected,
                            column=1,
                            editable=False,
                            value=high_counts_stats['number'],
                            format_str="{:d}")
        o_table.insert_item(row=row_selected,
                            column=2,
                            editable=False,
                            value=high_counts_stats['percentage'],
                            format_str="{:.2f}")

        dead_pixels_stats = o_algo.get_dead_pixels_stats()
        o_table.insert_item(row=row_selected,
                            column=3,
                            editable=False,
                            value=dead_pixels_stats['number'],
                            format_str="{:d}")
        o_table.insert_item(row=row_selected,
                            column=4,
                            editable=False,
                            value=dead_pixels_stats['percentage'],
                            format_str="{:.2f}")

        return o_algo.get_processed_data()

    def mouse_moved_in_any_image(self, position=None, image=None):        
        pos = position
        
        if image == 'raw':
            image_view = self.parent.ui.raw_image_view
        elif image == 'filtered':
            image_view = self.parent.ui.filtered_image_view
        else:
            image_view = self.parent.ui.diff_image_view

        if image_view.view.sceneBoundingRect().contains(pos):

            [height, width] = self.parent.image_size

            mouse_point = image_view.view.getViewBox().mapSceneToView(pos)
            mouse_x = int(mouse_point.x())
            mouse_y = int(mouse_point.y())

            if (0 <= mouse_x < width) and (0 <= mouse_y < height):
                self.parent.x_value.setText(str(mouse_x))
                self.parent.y_value.setText(str(mouse_y))

                _raw_value = self.parent.live_raw_image[mouse_x, mouse_y]
                _filtered_value = self.parent.live_filtered_image[mouse_x, mouse_y]

                self.parent.raw_value.setText("{:.02f}".format(_raw_value))
                self.parent.filtered_value.setText("{:.02f}".format(_filtered_value))

                self.parent.raw_hLine.setPos(mouse_point.y())
                self.parent.raw_vLine.setPos(mouse_point.x())
                self.parent.filtered_hLine.setPos(mouse_point.y())
                self.parent.filtered_vLine.setPos(mouse_point.x())

            else:
                self.parent.x_value.setText("N/A")
                self.parent.y_value.setText("N/A")
                self.parent.raw_value.setText("N/A")
                self.parent.filtered_value.setText("N/A")
