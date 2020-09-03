from __code.combine_images_with_outliners.combine_images import CombineImages
import pytest
import numpy as np


class TestCombineImagesWithOutliners:

	def test_raises_error_when_no_arrays(self):
		with pytest.raises(ValueError):
			CombineImages()

	def test_raises_error_if_less_than_3_arrays(self):
		list_array = [np.arange(10), np.arange(10)]
		with pytest.raises(ValueError):
			CombineImages(list_array=list_array)

	def test_make_sure_arrays_have_the_same_size(self):
		list_array = [np.arange(10), np.arange(9), np.arange(9)]
		with pytest.raises(ValueError):
			CombineImages.check_arrays_have_same_size(list_array=list_array)
