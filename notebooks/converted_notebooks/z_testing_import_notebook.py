# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Testing all imports
#
# Last release: 12/16/22 

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# * [bin images](bin_images.ipynb)

from bin.bin_images import BinHandler

# * [bragg edge normalization](bragg_edge_normalization.ipynb)    

from __code.bragg_edge.bragg_edge_normalization import BraggEdge

# * [bragg edge normalized sample and powder](bragg_edge_normalized_sample_and_powder.ipynb)

# * [bragg edge raw sample and powder](bragg_edge_raw_sample_and_powder.ipynb)

# * [bragg edge profile](bragg_edge_profile.ipynb)

# * [list element bragg edges](list_element_bragg_edges.ipynb)

# * [calibrated transmission](calibrated_transmission.ipynb)

# +
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_calibrated_transmission.ui')

# -

# * [circular profile of a ring](circular_profile_of_a_ring.ipynb)

# * [combine all images selected](combine_all_images_selected.ipynb)

# * [combine folders](combine_folders.ipynb)

# * [combine images n by n](combine_images_n_by_n.ipynb)

# * [combine images without outliers](combine_images_without_outliers.ipynb)

# * [create list of file name vs time stamp](create_list_of_file_name_vs_time_stamp.ipynb)

# * [cylindrical geometry correction](cylindrical_geometry_correction.ipynb)

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_profile.ui')

# * [deal images](deal_images.ipynb)

# * [display and export images with metadata profile](display_and_export_images_with_metadata_profile.ipynb)

from __code.display_and_export_images_with_metadata_profile import DisplayExportScreenshots

# * [display and export images with timestamp](display_and_export_images_with_timestamp.ipynb)

# * [display counts of region vs stack](display_counts_of_region_vs_stack.ipynb)

# +
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_display_counts_of_region_vs_stack.ui')

# -

# * [display file names vs time stamp](display_file_names_vs_time_stamp.ipynb)

from __code.display_file_names_vs_time_stamp import DisplayFileNamesVsTimeStamp

# * [display integrated stack of images](display_integrated_stack_of_images.ipynb)

from __code.display_integrated_stack_of_images import DisplayIntegratedStackOfImages

# * [dual energy](dual_energy.ipynb)

# * [extract evenly spaced files](extract_evenly_spaced_files.ipynb)

from __code.extract_evenly_spaced_files.interface_handler import Interface

# * [extract NeXus daslogs](extract_nexus_daslogs.ipynb)

# * [fix images](fix_images.ipynb)

# * [fix images with negative pixels](fix_images_with_negative_pixels.ipynb)

# * [from attenuation to concentration](from_attenuation_to_concentration.ipynb)

# * [from dsc_time info to ascii file vs time](from_dsc_time_info_to_ascii_file_vs_time.ipynb)

from __code.from_dsc_time_info_to_ascii_file_vs_time import CreateExportTimeStamp

# * [group images by cycle for panoramic stitching](group_images_by_cycle_for_panoramic_stitching.ipynb)

from __code.group_images_by_cycle_for_panoramic_stitching.group_images import GroupImages  

# * [group_images_by_cycle_for_grating_experiment](group_images_by_cycle_for_grating_experiment.ipynb)

# * [HFIR reactor element analysis](hfir_reactor_element_analysis.ipynb)

# * [images and metadata extrapolation matcher](images_and_metadata_extrapolation_matcher.ipynb)

from __code.images_and_metadata_extrapolation_matcher import ImagesAndMetadataExtrapolationMatcher

# * [integrated roi counts vs file name and time stamp](integrated_roi_counts_vs_file_name_and_time_stamp.ipynb)

o_builder = UiBuilder(ui_name = 'ui_integrated_roi_counts_vs_file_name_and_time_stamp.ui')
from __code.ipywe.myfileselector import FileSelection

# * [list element bragg edges](list_element_bragg_edges.ipynb)

# * [list metadata and time with oncat](list_metadata_and_time_with_oncat.ipynb)

# * [list tiff metadata](list_tiff_metadata.ipynb)

# * [math images](math_images.ipynb)

# * [mcp chips corrector](mcp_chips_corrector.ipynb)

# * [metadata ascii parser](metadata_ascii_parser.ipynb)

# * [metadata overlapping images](metadata_overlapping_images.ipynb)

# * [normalization](normalization.ipynb)

from __code.roi_selection_ui import Interface

# * [normalization with simplify selection](normalization_with_simplify_selection.ipynb)

# * [outliers filtering](outliers_filtering_tool.ipynb)

# * [overlay images](overlay_images.ipynb)

# * [panoramic stitching](panoramic_stitching.ipynb)

from __code.panoramic_stitching.panoramic_stitching import PanoramicStitching

# * [panoramic stitching for tof](panoramic_stitching_for_tof.ipynb)

# * [bragg edge profile](bragg_edge_profile.ipynb)

# * [profile](profile.ipynb)

o_builder = UiBuilder(ui_name = 'ui_profile.ui')
from __code.profile import ProfileUi

# * [radial profile](radial_profile.ipynb)

# * [water intake profile_calculator](water_intake_profile_calculator.ipynb)

o_builder = UiBuilder(ui_name = 'ui_water_intake_profile.ui')

# * [radial profile](radial_profile.ipynb)

# * [registration](registration.ipynb)

# * [rename files](rename_files.ipynb)

# * [resonance imaging experiment vs theory](resonance_imaging_experiment_vs_theory.ipynb)

# +
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_experiment_vs_theory.ui')
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_layers_input.ui')

# -

# * [roi statistics for a stack of images](roi_statistics_vs_stack.ipynb)

# * [rotate and crop images](rotate_and_crop_images.ipynb)

o_builder = UiBuilder(ui_name = 'ui_rotate_and_crop.ui')

# * [scale overlapping images](scale_overlapping_images.ipynb)

o_builder = UiBuilder(ui_name = 'ui_scale_overlapping_images.ui')
from __code.ipywe.myfileselector import FileSelection

# * [sequential combine images using metadata](sequential_combine_images_using_metadata.ipynb)

# * [shifting time offset](shifting_time_offset.ipynb)

from __code.select_files_and_folders import SelectFiles, SelectFolder

# * [water intake profile_calculator](water_intake_profile_calculator.ipynb)

o_builder = UiBuilder(ui_name = 'ui_water_intake_profile.ui')

# * [wave front dynamics](wave_front_dynamics.ipynb)


