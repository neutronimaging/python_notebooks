import numpy as np
from collections import defaultdict

from __code._panoramic_stitching.utilities import Utilities

DEBUG_JSON = False


class Stitching:

	def __init__(self, parent=None):
		self.parent = parent

	def run_fft(self):
		master_dict = self.parent.master_dict
		o_utilities = Utilities(parent=self.parent)

		for _row in master_dict.keys():

			_data_reference =  o_utilities.get_image_for_this_row(data_type='reference',
			                                                      row=_row)
			_data_target = o_utilities.get_image_for_this_row(data_type='target',
			                                                  row=_row)

			reference_roi = master_dict[_row]['reference_roi']
			[ref_x0, ref_y0, ref_width, ref_height] = Stitching.retrieve_roi_parameters(roi_dict=reference_roi)
			target_roi = master_dict[_row]['target_roi']
			[target_x0, target_y0, target_width, target_height] = Stitching.retrieve_roi_parameters(roi_dict=target_roi)

			_data_reference_roi = _data_reference[ref_y0:ref_y0+ref_height, ref_x0:ref_x0+ref_width]
			_data_target_roi = _data_target[target_y0:target_y0+target_height, target_x0:target_x0+target_width]

			f_reference = np.fft.fft2(_data_reference_roi)
			f_target = np.fft.fft2(_data_target_roi)

			f_ref_target = f_reference * np.conjugate(f_target)
			co = np.abs(np.fft.ifft2(f_ref_target))

			pos = np.where(co == np.amax(co))

			print("optimum x0:{} and optimum y0:{}".format(pos[0][0], pos[1][0]))





	def run(self):
		master_dict = self.parent.master_dict
		list_target_file = self.parent.list_target

		if DEBUG_JSON: roi_to_export = {}
		for _row in master_dict.keys():

			_data_reference = self.parent.list_reference['data'][_row]
			_target_file_index = master_dict[_row]['target_combobox_file_index']

			_target_file = list_target_file['files'][_target_file_index]
			_data_target = list_target_file['data'][_target_file_index]

			reference_roi = master_dict[_row]['reference_roi']
			[ref_x0, ref_y0, ref_width, ref_height] = Stitching.retrieve_roi_parameters(roi_dict=reference_roi)

			target_roi = master_dict[_row]['target_roi']
			[starting_target_x0, starting_target_y0, target_width, target_height] = \
				Stitching.retrieve_roi_parameters(roi_dict=target_roi)

			_data_reference_of_roi = _data_reference[ref_y0:ref_y0+ref_height, ref_x0:ref_x0+ref_width]

			# where to start from
			moving_target_x0 = starting_target_x0
			moving_target_y0 = starting_target_y0

			moving_target_width = ref_width
			moving_target_height = ref_height

			# where to end
			final_target_x0 = starting_target_x0 + target_width - ref_width
			final_target_y0 = starting_target_y0 + target_height - ref_height

			moving_target_x1 = moving_target_x0 + moving_target_width
			moving_target_y1 = moving_target_y0 + moving_target_height

			print("Reference:")
			print("x0:{}, y0:{}, width:{}, height:{}".format(ref_x0, ref_y0, ref_width, ref_height))
			print("target:")
			print("x0:{}, y0:{}, width:{}, height:{}".format(starting_target_x0, starting_target_y0,
			                                                 target_width, target_height))

			if DEBUG_JSON:
				o_utilities = Utilities(parent=self.parent)
				_reference_file_index = o_utilities.get_reference_index_selected_from_row(row=_row)

				roi_to_export[str(_row)] = {'reference': {'x0': str(ref_x0),
														  'y0': str(ref_y0),
														  'width': str(np.int(ref_width)),
														  'height': str(np.int(ref_height)),
														  'file_index': str(_target_file_index)},
											'target': {'x0': str(starting_target_x0),
													   'y0': str(starting_target_y0),
													   'width': str(np.int(target_width)),
													   'height': str(np.int(target_height)),
													   'file_index': str(_reference_file_index)}}

			counts_and_x0_position_dict = defaultdict(list)
			counts_and_y0_position_dict = defaultdict(list)

			counts_3d = np.zeros((final_target_y0 - moving_target_y0+1, final_target_x0 - moving_target_x0+1))

			x = 0
			y = 0
			while moving_target_y0 <= final_target_y0:

				_data_target_of_roi = _data_target[moving_target_y0:moving_target_y0+ref_height,
				                                   moving_target_x0:moving_target_x0+ref_width]

				_diff_array = np.abs(_data_target_of_roi - _data_reference_of_roi)
				_sum_diff_array = np.sum(_diff_array)
				counts_and_x0_position_dict[_sum_diff_array].append(moving_target_x0)
				counts_and_y0_position_dict[_sum_diff_array].append(moving_target_y0)

				counts_3d[y,x] = _sum_diff_array

				moving_target_x0 += 1
				x += 1
				if moving_target_x0 > final_target_x0:
					moving_target_x0 = starting_target_x0
					x = 0

					moving_target_y0 += 1
					y += 1

			list_of_counts_x0 = np.array(list(counts_and_x0_position_dict.keys()))
			list_of_counts_y0 = np.array(list(counts_and_y0_position_dict.keys()))
			optimum_counts_for_x0 = list_of_counts_x0.min()
			optimum_counts_for_y0 = list_of_counts_y0.min()

			# self.parent.debug_list_of_counts_x0 = list_of_counts_x0
			# self.parent.debug_list_of_counts_y0 = list_of_counts_y0
			self.parent.debug_counts_3d = counts_3d

			optimum_x0 = counts_and_x0_position_dict[optimum_counts_for_x0][0]
			optimum_y0 = counts_and_y0_position_dict[optimum_counts_for_y0][0]


			print("optimum x0:{} and optimum y0:{}".format(optimum_x0, optimum_y0))

			self.parent.debug_big_array_roi_ref = _data_reference_of_roi
			self.parent.debug_big_array_roi_target = _data_target[optimum_y0:optimum_y0+ref_height,
														   optimum_x0:optimum_x0+ref_width]

			if DEBUG_JSON:
				import json
				with open('/Users/j35/Desktop/roi.txt', 'w') as outfile:
					json.dump(roi_to_export, outfile)

	@staticmethod
	def retrieve_roi_parameters(roi_dict={}):
		_x0 = roi_dict['x0']
		_y0 = roi_dict['y0']
		_width = roi_dict['width']
		_height = roi_dict['height']
		return [_x0, _y0, _width, _height]
