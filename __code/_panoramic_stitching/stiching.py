import numpy as np
from collections import defaultdict


class Stitching:

	def __init__(self, parent=None):
		self.parent = parent

	def run(self):
		master_dict = self.parent.master_dict
		list_target_file = self.parent.list_target

		for _index_reference, _reference_file in enumerate(master_dict.keys()):

			_data_reference = self.parent.list_reference['data'][_index_reference]
			_target_file_index = master_dict[_reference_file]['associated_with_file_index']
			_target_file = list_target_file['files'][_target_file_index]
			_data_target = list_target_file['data'][_target_file_index]

			reference_roi = master_dict[_reference_file]['reference_roi']
			[ref_x0, ref_y0, ref_width, ref_height] = Stitching.retrieve_roi_parameters(roi_dict=reference_roi)

			target_roi = master_dict[_reference_file]['target_roi']
			[starting_target_x0, starting_target_y0, target_width, target_height] = Stitching.retrieve_roi_parameters(roi_dict=target_roi)

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

			counts_and_x0_position_dict = defaultdict(list)
			counts_and_y0_position_dict = defaultdict(list)
			while ((moving_target_x0 <= final_target_x0) and (moving_target_y0 <= final_target_y0)):


				# print("x0: {}, y0: {}".format(moving_target_x0, moving_target_y0), end=" -> ")

				_data_target_of_roi = _data_target[moving_target_y0:moving_target_y0+ref_height,
				                                   moving_target_x0:moving_target_x0+ref_width]

				_diff_array = np.abs(_data_target_of_roi - _data_reference_of_roi)
				_sum_diff_array = np.sum(_diff_array)
				counts_and_x0_position_dict[_sum_diff_array].append(moving_target_x0)
				counts_and_y0_position_dict[_sum_diff_array].append(moving_target_y0)

				# print("np.shape(_data_target_of_roi): {}".format(np.shape(_data_target_of_roi)))

				moving_target_x0 += 1
				if moving_target_x0 > final_target_x0:
					moving_target_x0 = starting_target_x0

					moving_target_y0 += 1
					if moving_target_y0 > final_target_y0:
						break

			import pprint
			pprint.pprint(counts_and_x0_position_dict)
			pprint.pprint(counts_and_y0_position_dict)



	def retrieve_roi_parameters(roi_dict={}):
		_x0 = roi_dict['x0']
		_y0 = roi_dict['y0']
		_width = roi_dict['width']
		_height = roi_dict['height']
		return [_x0, _y0, _width, _height]