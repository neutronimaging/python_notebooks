import numpy as np

from __code._utilities.get import Get as TopGet
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.selection_region_utilities import SelectionRegionUtilities
from __code.bragg_edge.peak_fitting_evaluation import LOG_FILENAME


class GetInfo(TopGet):

    def log_file_name(self):
        return TopGet.log_file_name(LOG_FILENAME)


class Get(TopGet):

    def __init__(self, parent=None):
        self.parent = parent

        self.x_axis_choice_ui = {'selection': {'index' : self.parent.ui.selection_index_radiobutton,
                                               'tof'   : self.parent.ui.selection_tof_radiobutton,
                                               'lambda': self.parent.ui.selection_lambda_radiobutton},
                                 'fitting'  : {'index' : self.parent.ui.fitting_index_radiobutton,
                                               'tof'   : self.parent.ui.fitting_tof_radiobutton,
                                               'lambda': self.parent.ui.fitting_lambda_radiobutton},
                                 }

    def specified_x_axis(self, xaxis='index'):
        # if self.parent.is_file_imported:
        # 	return self.parent.fitting_input_dictionary['xaxis'][xaxis]
        # else:
        label = self.parent.xaxis_label[xaxis]
        if xaxis == 'index':
            return self.parent.index_array, label
        elif xaxis == 'tof':
            return self.parent.tof_array_s * 1e6, label
        elif xaxis == 'lambda':
            return self.parent.lambda_array, label
        else:
            raise NotImplementedError

    def x_axis_label(self, x_axis_selected='index'):
        x_axis_dict = self.parent.fitting_input_dictionary['xaxis']
        return x_axis_dict[x_axis_selected][1]

    def x_axis_checked(self):
        o_gui = GuiUtility(parent=self)
        tab_selected = o_gui.get_tab_selected(tab_ui=self.parent.ui.tabWidget).lower()

        list_ui = self.x_axis_choice_ui[tab_selected]

        if list_ui['index'].isChecked():
            return 'index'
        elif list_ui['tof'].isChecked():
            return 'tof'
        else:
            return 'lambda'

    def x_axis(self):
        o_gui = GuiUtility(parent=self.parent)
        tab_selected = o_gui.get_tab_selected(self.parent.ui.tabWidget).lower()

        list_ui = self.x_axis_choice_ui[tab_selected]
        if list_ui['index'].isChecked():
            return self.specified_x_axis(xaxis='index')
        elif list_ui['tof'].isChecked():
            return self.specified_x_axis(xaxis='tof')
        else:
            return self.specified_x_axis(xaxis='lambda')

    def all_x_axis(self):
        all_x_axis = {'index' : self.specified_x_axis(xaxis='index'),
                      'tof'   : self.specified_x_axis(xaxis='tof'),
                      'lambda': self.specified_x_axis(xaxis='lambda')}
        return all_x_axis

    def all_russian_doll_region_full_infos(self):
        if self.parent.is_file_imported:
            dict_regions = self.parent.fitting_input_dictionary['rois']
        else:
            # collect initial selection size (x0, y0, width, height)
            [x0, y0, x1, y1, width, height] = self.selection_roi_dimension()
            # create profile for all the fitting region inside that first box
            o_regions = SelectionRegionUtilities(x0=x0, y0=y0, width=width, height=height)
            dict_regions = o_regions.get_all_russian_doll_regions()
            self.parent.add_profile_to_dict_of_all_regions(dict_regions=dict_regions)
        return dict_regions

    def selection_roi_dimension(self):
        roi_id = self.parent.roi_id

        x0, y0, x1, y1, width, height = None, None, None, None, None, None

        if roi_id:
            region = roi_id.getArraySlice(self.parent.final_image,
                                          self.parent.ui.image_view.imageItem)
            x0 = region[0][0].start
            x1 = region[0][0].stop
            y0 = region[0][1].start
            y1 = region[0][1].stop
            width = int(x1 - x0)
            height = int(y1 - y0)

        else:
            x0, y0, x1, y1, width, height = self.parent.roi_dimension_from_config_file

        return [x0, y0, x1, y1, width, height]

    def profile_of_roi(self, x0=None, y0=None, x1=None, y1=None, width=None, height=None):
        profile_value = []

        if width:
            x1 = x0 + width
        if height:
            y1 = y0 + height

        for _image in self.parent.o_norm.data['sample']['data']:
            _value = np.mean(_image[y0:y1, x0:x1])
            profile_value.append(_value)

        return profile_value

    def requested_xaxis(self, xaxis_label='index'):
        if xaxis_label == 'index':
            return self.parent.dict_profile_to_fit['xaxis']['index'], self.parent.xaxis_label['index']
        elif xaxis_label == 'tof':
            return self.parent.dict_profile_to_fit['xaxis']['tof'], self.parent.xaxis_label['tof']
        elif xaxis_label == 'lambda':
            return self.parent.dict_profile_to_fit['xaxis']['lambda'], self.parent.xaxis_label['lambda']

    def fitting_profile_xaxis(self):
        if self.parent.ui.fitting_tof_radiobutton.isChecked():
            return self.requested_xaxis(xaxis_label='tof')
        elif self.ui.fitting_index_radiobutton.isChecked():
            return self.requested_xaxis(xaxis_label='index')
        else:
            return self.requested_xaxis(xaxis_label='lambda')

    def part_of_fitting_selected(self):
        """high, low or bragg_peak"""
        list_pages = ["Bragg peak selection", "high", "low", "bragg_peak"]
        list_table_ui = [None,
                         self.parent.ui.high_lda_tableWidget,
                         self.parent.ui.low_lda_tableWidget,
                         self.parent.ui.bragg_edge_tableWidget]

        page_index = self.parent.ui.kropff_toolBox.currentIndex()

        return {'name_of_page': list_pages[page_index],
                'table_ui'    : list_table_ui[page_index]}

    def y_axis_data_of_selected_row(self, row_selected):
        selected_roi = self.parent.fitting_input_dictionary['rois'][row_selected]
        yaxis = selected_roi['profile']
        [left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
        yaxis = yaxis[left_xaxis_index: right_xaxis_index]
        return yaxis

    def x_axis_data(self, x_axis_selected='index'):
        xaxis_dict = self.parent.fitting_input_dictionary['xaxis']
        xaxis_index, xaxis_label = xaxis_dict[x_axis_selected]
        [left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
        xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]
        return xaxis

    def march_dollase_result_fitting_item_selected(self):
        if self.parent.ui.march_d_spacing.isChecked():
            return 'd_spacing'
        elif self.parent.ui.march_sigma.isChecked():
            return 'sigma'
        elif self.parent.ui.march_alpha.isChecked():
            return 'alpha'
        elif self.parent.ui.march_a1.isChecked():
            return 'a1'
        elif self.parent.ui.march_a2.isChecked():
            return 'a2'
        elif self.parent.ui.march_a5.isChecked():
            return 'a5'
        elif self.parent.ui.march_a6.isChecked():
            return 'a6'
        else:
            raise NotImplementedError("fitting option parameter not implemented!")

    @staticmethod
    def units(name='index'):
        if name == 'index':
            return 'file index'
        elif name == 'tof':
            return u"\u03BCs"
        elif name == 'lambda':
            return u"\u212B"
        else:
            return ""
