class CombineImages:

	def __init__(self, list_array=None):
		if list_array is None:
			raise ValueError("Please provide a list of arrays!")

		# in future implementation, we may do something else when less than 3 arrays are provided
		if len(list_array) < 3:
			raise ValueError("Please provide at least 3 arrays!")

		self.check_arrays_have_same_size(list_array=list_array)

	@staticmethod
	def check_arrays_have_same_size(list_array=None):
		list_len_array = set([len(_array) for _array in list_array])
		if len(list_len_array) > 1:
			raise ValueError("Arrays do not have the same size!")
