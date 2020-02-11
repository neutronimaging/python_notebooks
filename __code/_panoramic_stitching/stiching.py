class Stitching:

	def __init__(self, parent=None):
		self.parent = parent

	def run(self):
		master_dict = self.parent.master_dict
		list_target_file = self.parent.list_reference.keys()

		for _index_reference, _reference_file in enumerate(master_dict.keys()):

			_data_reference = self.parent.list_reference[_reference_file]['data']
			_target_file_index = master_dict[_reference_file]['associated_with_file_index']
			_target_file = list_target_file[_target_file_index]
			_data_target = self.parent.list_target[_target_file]

			reference_roi = master_dict[_data_reference]['reference_roi']
			ref_x0 = reference_roi['x0']
			ref_y0 = reference_roi['y0']
			ref_width = reference_roi['width']
			ref_height = reference_roi['height']

			target_roi = master_dict[_data_reference]['target_roi']

			_data_reference_of_roi = _data_reference[ref_y0:ref_y0+ref_height, ref_x0:ref_x0+ref_width]
