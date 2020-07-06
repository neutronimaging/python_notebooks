from IPython.core.display import HTML
import os
import random
import numpy as np
from IPython.display import display
import pyqtgraph as pg
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui, QtCore

from neutronbraggedge.experiment_handler import *

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code import load_ui
from __code.utilities import find_nearest_index


DEBUGGING = True


class BraggEdge(BraggEdgeParent):
   pass


class Interface(QMainWindow):

    bragg_edge_range = [5, 20]
    roi_settings = {'color': QtGui.QColor(62, 13, 244),
                    'width': 0.01,
                    'position': [10, 10]}
    shrinking_roi_settings = {'color': QtGui.QColor(13, 214, 244),
                              'width': 0.01,
                              'dashes_pattern': [4, 2]}
    image_size = {'width': None,
                  'height': None}
    roi_id = None
    xaxis_label = {'index': "File index",
                   'tof': u"TOF (\u00B5s)",
                   'lambda': u"\u03BB (\u212B)"}
    fitting_rois = {'kropff': {'step1': None,
                               'step2': None,
                               'step3': None,
                               },
                    }

    def __init__(self, parent=None, o_norm=None, spectra_file=None):

        self.o_norm = o_norm
        self.spectra_file = spectra_file

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_bragg_edge_peak_fitting.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Peak Fitting Tool")

        # initialization
        o_init = Initialization(parent=self)
        o_init.display(image=self.get_live_image())
        self.load_time_spectra()
        self.roi_moved()

    def load_time_spectra(self):
        self.tof_handler = TOF(filename=self.spectra_file)
        self.update_time_spectra()

    def update_time_spectra(self):
        _exp = Experiment(tof=self.tof_handler.tof_array,
                          distance_source_detector_m=np.float(self.ui.distance_detector_sample.text()),
                          detector_offset_micros=np.float(self.ui.detector_offset.text()))
        self.lambda_array = _exp.lambda_array * 1e10  # to be in Angstroms
        self.tof_array = self.tof_handler.tof_array

    def get_live_image(self):
        if DEBUGGING:
            final_array = self.o_norm.data['sample']['data']
        else:
            nbr_data_to_use = np.int(self.number_of_data_to_use_ui.value)

            _data = self.o_norm.data['sample']['data']

            nbr_images = len(_data)
            list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)

            final_array = []
            for _index in list_of_indexes_to_keep:
                final_array.append(_data[_index])

        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image
        return final_image

    @staticmethod
    def check_size(x_axis=None, y_axis=None):
        size_x = len(x_axis)
        size_y = len(y_axis)
        min_len = np.min([size_x, size_y])
        return x_axis[:min_len], y_axis[:min_len]

    def roi_moved(self):
        self.update_selection_profile_plot()
        self.update_all_size_widgets_infos()
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def update_all_size_widgets_infos(self):
        roi_id = self.roi_id
        region = roi_id.getArraySlice(self.final_image,
                                      self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        new_width = x1-x0-1
        new_height = y1-y0-1

        self.ui.roi_width.setText(str(new_width))
        self.ui.roi_height.setText(str(new_height))
        self.ui.profile_of_bin_size_width.setText(str(new_width))
        self.ui.profile_of_bin_size_height.setText(str(new_height))

        max_value = np.min([new_width, new_height])
        self.ui.profile_of_bin_size_slider.setValue(max_value)
        self.ui.profile_of_bin_size_slider.setMaximum(max_value)

    def get_x_axis(self):
        o_gui = GuiUtility(parent=self)
        tab_selected = o_gui.get_tab_selected().lower()

        x_axis_choice_ui = {'selection': {'index': self.ui.selection_index_radiobutton,
                                          'tof': self.ui.selection_tof_radiobutton,
                                          'lambda': self.ui.selection_lambda_radiobutton},
                            'fitting': {'index': self.ui.fitting_index_radiobutton,
                                        'tof': self.ui.fitting_tof_radiobutton,
                                        'lambda': self.ui.fitting_lambda_radiobutton},
                            }

        list_ui = x_axis_choice_ui[tab_selected]

        if list_ui['index'].isChecked():
            return self.get_specified_x_axis(xaxis='index')
        elif list_ui['tof'].isChecked():
            return self.get_specified_x_axis(xaxis='tof')
        else:
            return self.get_specified_x_axis(xaxis='lambda')

    def get_specified_x_axis(self, xaxis='index'):
        label = self.xaxis_label[xaxis]
        if xaxis == 'index':
            return np.arange(len(self.o_norm.data['sample']['file_name'])), label
        elif xaxis == 'tof':
            return self.tof_array * 1e6, label
        elif xaxis == 'lambda':
            return self.lambda_array, label
        else:
            raise NotImplementedError

    def get_all_x_axis(self):
        all_x_axis = {'index': self.get_specified_x_axis(xaxis='index'),
                      'tof': self.get_specified_x_axis(xaxis='tof'),
                      'lambda': self.get_specified_x_axis(xaxis='lambda')}
        return all_x_axis

    def get_selection_roi_dimension(self):
        roi_id = self.roi_id
        region = roi_id.getArraySlice(self.final_image,
                                      self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        return [x0, y0, x1, y1]

    def update_selection_profile_plot(self):
        [x0, y0, x1, y1] = self.get_selection_roi_dimension()
        profile = self.get_profile_of_roi(x0, y0, x1, y1)

        x_axis, x_axis_label = self.get_x_axis()
        
        x_axis, y_axis = Interface.check_size(x_axis=x_axis,
                                              y_axis=profile)

        self.ui.profile.clear()
        self.ui.profile.plot(x_axis, y_axis)
        self.ui.profile.setLabel("bottom", x_axis_label)
        self.ui.profile.setLabel("left", 'Mean counts')

        bragg_edge_range = [x_axis[self.bragg_edge_range[0]],
                            x_axis[self.bragg_edge_range[1]]]

        self.bragg_edge_range_ui = pg.LinearRegionItem(values=bragg_edge_range,
                                                       orientation=None,
                                                       brush=None,
                                                       movable=True,
                                                       bounds=None)
        self.bragg_edge_range_ui.sigRegionChanged.connect(self.bragg_edge_range_changed)
        self.bragg_edge_range_ui.setZValue(-10)
        self.ui.profile.addItem(self.bragg_edge_range_ui)

    def bragg_edge_range_changed(self):
        [left_range, right_range] = list(self.bragg_edge_range_ui.getRegion())
        x_axis, _ = self.get_x_axis()

        left_index = find_nearest_index(array=x_axis, value=left_range)
        right_index = find_nearest_index(array=x_axis, value=right_range)

        self.bragg_edge_range = [left_index, right_index]

    def get_profile_of_roi(self, x0, y0, x1, y1):

        profile_value = []
        for _image in self.o_norm.data['sample']['data']:
            _value = np.mean(_image[y0:y1, x0:x1])
            profile_value.append(_value)

        return profile_value

    # event handler
    def roi_radiobuttons_changed(self):
        if self.ui.square_roi_radiobutton.isChecked():
            slider_visible = True
            new_width = np.min([np.int(str(self.ui.roi_width.text())),
                                np.int(str(self.ui.roi_height.text()))])
            self.selection_roi_slider_changed(new_width)
        else:
            slider_visible = False
            new_value = np.int(str(self.ui.roi_width.text()))
            self.update_2d_free_roi(new_value)
        self.ui.roi_size_slider.setVisible(slider_visible)

        self.reset_profile_of_bin_size_slider()
        self.update_roi_defined_by_profile_of_bin_size_slider()

        # # reset profile of bin size slider
        # [x0, y0, x1, y1] = self.get_selection_roi_dimension()
        # width = np.int(x1-x0)
        # height = np.int(y1-y0)
        # _pen = QtGui.QPen()
        # _pen.setColor(self._color_shrinking_roi)
        # _pen.setWidth(self.shrinking_roi_settings['width'])
        # self.shrinking_roi_id = pg.ROI([x0, y0],
        #                                [width, height],
        #                                pen=_pen,
        #                                scaleSnap=True)
        # self.ui.image_view.addItem(self.shrinking_roi_id)


    def reset_profile_of_bin_size_slider(self):
        max_value = np.min([np.int(str(self.ui.profile_of_bin_size_width.text())),
                            np.int(str(self.ui.profile_of_bin_size_height.text()))])
        self.ui.profile_of_bin_size_slider.setMaximum(max_value)
        self.ui.profile_of_bin_size_slider.setValue(max_value)

    def update_2d_free_roi(self, new_value):
        region = self.roi_id.getArraySlice(self.final_image, self.ui.image_view.imageItem)

        x0 = region[0][0].start
        y0 = region[0][1].start

        # remove old one
        self.ui.image_view.removeItem(self.roi_id)
        # self.ui.image_view.removeItem(self.shrinking_roi_id)

        _pen = QtGui.QPen()
        _pen.setColor(self.roi_settings['color'])
        _pen.setWidth(self.roi_settings['width'])
        self.roi_id = pg.ROI([x0, y0],
                             [new_value, new_value],
                             pen=_pen,
                             scaleSnap=True)
        self.ui.image_view.addItem(self.roi_id)
        self.roi_id.addScaleHandle([1, 1], [0, 0])
        self.roi_id.sigRegionChanged.connect(self.roi_moved)
        self.update_selection_profile_plot()

    def selection_roi_slider_changed(self, new_value):
        if self.roi_id is None:
            return
        self.ui.roi_width.setText(str(new_value))
        self.ui.roi_height.setText(str(new_value))

        region = self.roi_id.getArraySlice(self.final_image, self.ui.image_view.imageItem)

        x0 = region[0][0].start
        y0 = region[0][1].start
        self.selection_x0y0 = [x0, y0]

        # remove old one
        self.ui.image_view.removeItem(self.roi_id)

        _pen = QtGui.QPen()
        _pen.setColor(self.roi_settings['color'])
        _pen.setWidth(self.roi_settings['width'])
        self.roi_id = pg.ROI([x0, y0],
                             [new_value, new_value],
                             pen=_pen,
                             scaleSnap=True)
        self.ui.image_view.addItem(self.roi_id)
        self.roi_id.sigRegionChanged.connect(self.roi_moved)
        self.reset_profile_of_bin_size_slider()
        self.update_selection_profile_plot()
        self.update_profile_of_bin_size_infos()
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def update_profile_of_bin_size_infos(self):
        _width = np.int(self.ui.roi_width.text())
        _height = np.int(self.ui.roi_height.text())
        self.ui.profile_of_bin_size_width.setText(str(_width))
        self.ui.profile_of_bin_size_height.setText(str(_height))
        self.ui.profile_of_bin_size_slider.setValue(np.min([_width, _height]))

    def distance_detector_sample_changed(self):
        self.update_time_spectra()
        self.update_selection_profile_plot()

    def detector_offset_changed(self):
        self.update_time_spectra()
        self.update_selection_profile_plot()

    def selection_axis_changed(self):
        self.update_selection_profile_plot()

    def fitting_axis_changed(self):
        self.update_selection_profile_plot()

    def fit_that_selection_pushed(self):
        [left_range, right_range] = self.bragg_edge_range

        [x0, y0, x1, y1] = self.get_selection_roi_dimension()
        profile = self.get_profile_of_roi(x0, y0, x1, y1)

        yaxis = profile[left_range: right_range]

        all_x_axis = self.get_all_x_axis()
        index_array = all_x_axis['index'][0]
        tof_array = all_x_axis['tof'][0]
        lambda_array = all_x_axis['lambda'][0]

        index_selected = index_array[left_range: right_range]
        tof_selected = tof_array[left_range: right_range]
        lambda_selected = lambda_array[left_range: right_range]

        profile_to_fit = {'yaxis': yaxis,
                          'xaxis': {'index': index_selected,
                                    'tof': tof_selected,
                                    'lambda': lambda_selected},
                          }
        self.dict_profile_to_fit = profile_to_fit
        self.update_fitting_plot()

        self.reset_fitting_rois = {'kropff': {'step1': None,
                                              'step2': None,
                                              'step3': None,
                                             },
                                  }

    def update_fitting_plot(self):
        x_axis, x_axis_label = self.get_fitting_profile_xaxis()
        profile = self.dict_profile_to_fit['yaxis']
        x_axis, y_axis = Interface.check_size(x_axis=x_axis,
                                              y_axis=profile)
        self.ui.fitting.clear()
        self.ui.fitting.plot(x_axis, y_axis)
        self.ui.fitting.setLabel("bottom", x_axis_label)
        self.ui.fitting.setLabel("left", 'Mean counts')

        # bragg_edge_range = [x_axis[self.bragg_edge_range[0]],
        #                     x_axis[self.bragg_edge_range[1]]]
        #
        # self.bragg_edge_range_ui = pg.LinearRegionItem(values=bragg_edge_range,
        #                                                orientation=None,
        #                                                brush=None,
        #                                                movable=True,
        #                                                bounds=None)
        # self.bragg_edge_range_ui.sigRegionChanged.connect(self.bragg_edge_range_changed)
        # self.bragg_edge_range_ui.setZValue(-10)
        # self.ui.profile.addItem(self.bragg_edge_range_ui)

    def get_fitting_profile_xaxis(self):
        if self.ui.fitting_tof_radiobutton.isChecked():
            return self.dict_profile_to_fit['xaxis']['tof'], self.xaxis_label['tof']
        elif self.ui.fitting_index_radiobutton.isChecked():
            return self.dict_profile_to_fit['xaxis']['index'], self.xaxis_label['index']
        else:
            return self.dict_profile_to_fit['xaxis']['lambda'], self.xaxis_label['lambda']

    def profile_of_bin_size_slider_changed(self, new_value):
        if self.ui.square_roi_radiobutton.isChecked():
            new_width = new_value
            new_height = new_value
        else:
            initial_roi_width = np.int(str(self.ui.roi_width.text()))
            initial_roi_height = np.int(str(self.ui.roi_height.text()))
            if initial_roi_width == initial_roi_height:
                new_width = new_value
                new_height = new_value
            elif initial_roi_width < initial_roi_height:
                new_width = new_value
                delta = initial_roi_width - new_width
                new_height = initial_roi_height - delta
            else:
                new_height = new_value
                delta = initial_roi_height - new_height
                new_width = initial_roi_width - delta

        self.ui.profile_of_bin_size_width.setText(str(new_width))
        self.ui.profile_of_bin_size_height.setText(str(new_height))
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def update_roi_defined_by_profile_of_bin_size_slider(self):
        coordinates_new_selection = self.get_coordinates_of_new_inside_selection_box()
        x0 = coordinates_new_selection['x0']
        y0 = coordinates_new_selection['y0']
        width = coordinates_new_selection['width']
        height = coordinates_new_selection['height']

        # remove old selection

        # plot new box
        _pen = QtGui.QPen()
        _pen.setDashPattern(self.shrinking_roi_settings['dashes_pattern'])
        _pen.setColor(self.shrinking_roi_settings['color'])


    def get_coordinates_of_new_inside_selection_box(self):
        # get width and height defined in fitting labels (top right)
        width_requested = np.int(str(self.ui.profile_of_bin_size_width.text()))
        height_requested = np.int(str(self.ui.profile_of_bin_size_height.text()))

        # retrieve x0, y0, width and height of full selection
        [x0, y0] = self.selection_x0y0
        width_full_selection = np.int(str(self.ui.roi_width.text()))
        height_full_selection = np.int(str(self.ui.roi_height.text()))

        delta_width = width_full_selection - width_requested
        delta_height = height_full_selection - height_requested

        new_x0 = x0 + np.int(delta_width / 2)
        new_y0 = y0 + np.int(delta_height / 2)

        return {'x0': new_x0, 'y0': new_y0, 'width': width_requested, 'height': height_requested}

    def export_all_profiles_button_clicked(self):
        pass

    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
