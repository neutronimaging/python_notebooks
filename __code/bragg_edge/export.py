from pathlib import Path
from qtpy.QtWidgets import QFileDialog

from __code.bragg_edge.get import Get
from __code.file_handler import make_ascii_file


class Export:

	def __init__(self, parent=None):
		self.parent = parent

	def configuration(self):
		# bring file dialog to locate where the file will be saved
		base_folder = Path(self.parent.working_dir)
		directory = str(base_folder.parent)
		_export_folder = QFileDialog.getExistingDirectory(self.parent,
		                                                  directory=directory,
		                                                  caption="Select Output Folder",
		                                                  options=QFileDialog.ShowDirsOnly)

		if _export_folder:
			data, metadata = self.get_data_metadata_from_selection_tab()

			# collect initial selection size (x0, y0, width, height)
			[x0, y0, x1, y1, width, height] = self.get_selection_roi_dimension()

			name_of_ascii_file = Export.makeup_name_of_profile_ascii_file(base_name=str(base_folder.name),
			                                                                 export_folder=_export_folder,
			                                                                 x0=x0, y0=y0,
			                                                                 width=width,
			                                                                 height=height)

			make_ascii_file(metadata=metadata,
			                data=data,
			                output_file_name=name_of_ascii_file,
			                dim='1d')

			self.parent.ui.statusbar.showMessage("{} has been created!".format(name_of_ascii_file), 10000)  # 10s
			self.parent.ui.statusbar.setStyleSheet("color: green")

	@staticmethod
	def makeup_name_of_profile_ascii_file(base_name="default",
	                                      export_folder="./",
	                                      x0=None, y0=None, width=None, height=None):
		"""this will return the full path name of the ascii file to create that will contain all the profiles
		starting with the selection box and all the way to the minimal size"""
		full_base_name = "full_set_of_shrinkable_region_profiles_from_" + \
		                 "x{}_y{}_w{}_h{}_for_folder_{}.txt".format(x0, y0, width, height, base_name)
		return str(Path(export_folder) / full_base_name)

	def get_data_metadata_from_selection_tab(self):
		base_folder = Path(self.parent.working_dir)
		o_get = Get(parent=self.parent)

		index_axis, _ = o_get.specified_x_axis(xaxis='index')
		tof_axis, _ = o_get.specified_x_axis(xaxis='tof')
		lambda_axis, _ = o_get.specified_x_axis('lambda')
		fitting_peak_range = self.parent.bragg_edge_range
		distance_detector_sample = str(self.parent.ui.distance_detector_sample.text())
		detector_offset = str(self.parent.ui.detector_offset.text())

		dict_regions = self.get_all_russian_doll_region_full_infos()
		metadata = Interface.make_metadata(base_folder=base_folder,
		                                   fitting_peak_range=fitting_peak_range,
		                                   dict_regions=dict_regions,
		                                   distance_detector_sample=distance_detector_sample,
		                                   detector_offset=detector_offset)
		self.add_fitting_infos_to_metadata(metadata)

		metadata.append("#")
		metadata.append("#File Index, TOF(micros), lambda(Angstroms), ROIs (see above)")
		data = Interface.format_data(col1=index_axis,
		                             col2=tof_axis,
		                             col3=lambda_axis,
		                             dict_regions=dict_regions)

		return data, metadata

