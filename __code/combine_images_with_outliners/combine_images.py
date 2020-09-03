import numpy as np


class CombineImages:

	def __init__(self, list_array=None):
		if list_array is None:
			raise ValueError("Please provide a list of arrays!")

		# in future implementation, we may do something else when less than 3 arrays are provided
		if len(list_array) < 3:
			raise ValueError("Please provide at least 3 arrays!")

		self.check_arrays_have_same_size_and_dimensions(list_array=list_array)

	@staticmethod
	def check_arrays_have_same_size_and_dimensions(list_array=None):
		list_len_array = set([len(_array) for _array in list_array])
		if len(list_len_array) > 1:
			raise ValueError("Arrays do not have the same size!")

		# make sure all the dimensions have the same size
		list_shape_array = set([_array.shape for _array in list_array])
		if len(list_shape_array) > 1:
			raise ValueError("Arrays do not have the same dimension!")

	@staticmethod
	def mean_without_outliers(list_array=None):
		global_array = []
		for _array in list_array:
			global_array.append(_array)
		nbr_arrays = len(global_array)

		min_array = np.min(global_array, 0)
		max_array = np.max(global_array, 0)

		sum_array = np.sum(global_array, 0) - max_array - min_array
		mean_array = sum_array / (nbr_arrays - 2)

		return mean_array
