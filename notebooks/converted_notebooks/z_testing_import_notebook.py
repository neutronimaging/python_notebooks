# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
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

from __code.bin_images import BinHandler

# * [bragg edge normalization](bragg_edge_normalization.ipynb)    

from __code.bragg_edge.bragg_edge_normalization import BraggEdge

# * [bragg edge normalized sample and powder](bragg_edge_normalized_sample_and_powder.ipynb)

from __code.bragg_edge.bragg_edge import BraggEdge, Interface

# * [bragg edge raw sample and powder](bragg_edge_raw_sample_and_powder.ipynb)

from __code.bragg_edge.bragg_edge_raw_sample_and_powder import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

# * [bragg edge profile](bragg_edge_profile.ipynb)

from __code.bragg_edge.bragg_edge_normalization import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

# * [list element bragg edges](list_element_bragg_edges.ipynb)

from __code.bragg_edge.bragg_edge import BraggEdge, Interface

# * [calibrated transmission](calibrated_transmission.ipynb)

# +
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_calibrated_transmission.ui')

from __code.ipywe.myfileselector import FileSelection
from __code.calibrated_transmission import CalibratedTransmissionUi
# -

# * [circular profile of a ring](circular_profile_of_a_ring.ipynb)

from __code.circular_profile_of_a_ring.interface_handler import InterfaceHandler
from __code.circular_profile_of_a_ring.circular_profile_of_a_ring import CircularProfileOfARing

# * [combine all images selected](combine_all_images_selected.ipynb)

from __code.combine_images import CombineImages

# * [combine folders](combine_folders.ipynb)

from __code.combine_folders import CombineFolders

# * [combine images n by n](combine_images_n_by_n.ipynb)

from __code.combine_images_n_by_n.combine_images_n_by_n import CombineImagesNByN as CombineImages

# * [combine images without outliers](combine_images_without_outliers.ipynb)

from __code.combine_images_without_outliers.combine_images import Interface

# * [create list of file name vs time stamp](create_list_of_file_name_vs_time_stamp.ipynb)

from __code.create_list_of_file_name_vs_time_stamp import CreateListFileName

# * [cylindrical geometry correction](cylindrical_geometry_correction.ipynb)

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_profile.ui')
from __code.ipywe.myfileselector import FileSelection
from __code.profile import ProfileUi

# * [deal images](deal_images.ipynb)

from __code.deal import Deal

# * [display and export images with metadata profile](display_and_export_images_with_metadata_profile.ipynb)

from __code.display_and_export_images_with_metadata_profile import DisplayExportScreenshots

# * [display and export images with timestamp](display_and_export_images_with_timestamp.ipynb)

from __code.display_and_export_images_with_time_stamp import DisplayExportScreenshots

# * [display counts of region vs stack](display_counts_of_region_vs_stack.ipynb)

# +
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_display_counts_of_region_vs_stack.ui')

from __code.display_counts_of_region_vs_stack import ImageWindow, DisplayCountsVsStack
# -

# * [display file names vs time stamp](display_file_names_vs_time_stamp.ipynb)

from __code.display_file_names_vs_time_stamp import DisplayFileNamesVsTimeStamp

# * [display integrated stack of images](display_integrated_stack_of_images.ipynb)

from __code.display_integrated_stack_of_images import DisplayIntegratedStackOfImages

# * [dual energy](dual_energy.ipynb)

from __code.dual_energy.dual_energy import Interface, DualEnergy

# * [extract evenly spaced files](extract_evenly_spaced_files.ipynb)

from __code.extract_evenly_spaced_files.main import ExtractEvenlySpacedFiles as EESF
from __code.extract_evenly_spaced_files.interface_handler import Interface

# * [extract NeXus daslogs](extract_nexus_daslogs.ipynb)

from __code.extract_nexus_daslogs import extract

# * [fix images](fix_images.ipynb)

from __code.fix_images import FixImages

# * [fix images with negative pixels](fix_images_with_negative_pixels.ipynb)

from __code.fix_images_with_negative_pixels import FixImages

# * [from attenuation to concentration](from_attenuation_to_concentration.ipynb)

from __code.from_attenuation_to_concentration import *

# * [from dsc_time info to ascii file vs time](from_dsc_time_info_to_ascii_file_vs_time.ipynb)

from __code.from_dsc_time_info_to_ascii_file_vs_time import CreateExportTimeStamp

# * [group images by cycle for panoramic stitching](group_images_by_cycle_for_panoramic_stitching.ipynb)

from __code.group_images_by_cycle_for_panoramic_stitching.group_images import GroupImages  

# * [group_images_by_cycle_for_grating_experiment](group_images_by_cycle_for_grating_experiment.ipynb)

from __code.group_images_by_cycle_for_grating_experiment.group_images import GroupImages

# * [HFIR reactor element analysis](hfir_reactor_element_analysis.ipynb)

from __code.hfir_reactor_element_analysis.hfir_reactor_element_analysis import HfirReactorElementAnalysis
from __code.hfir_reactor_element_analysis.interface_handler import InterfaceHandler

# * [images and metadata extrapolation matcher](images_and_metadata_extrapolation_matcher.ipynb)

from __code.select_files_and_folders import SelectAsciiFile, SelectFolder
from __code.images_and_metadata_extrapolation_matcher import ImagesAndMetadataExtrapolationMatcher

# * [integrated roi counts vs file name and time stamp](integrated_roi_counts_vs_file_name_and_time_stamp.ipynb)

o_builder = UiBuilder(ui_name = 'ui_integrated_roi_counts_vs_file_name_and_time_stamp.ui')
from __code.ipywe.myfileselector import FileSelection
from __code.integrated_roi_counts_vs_file_name_and_time_stamp import IntegratedRoiUi

# * [list element bragg edges](list_element_bragg_edges.ipynb)

from __code.bragg_edge.bragg_edge import BraggEdge, Interface

# * [list metadata and time with oncat](list_metadata_and_time_with_oncat.ipynb)

from __code.select_files_and_folders import SelectFiles, SelectFolder
from __code.list_metadata_and_time_with_oncat import ListMetadata

# * [list tiff metadata](list_tiff_metadata.ipynb)

from __code.select_metadata_to_display import DisplayMetadata

# * [math images](math_images.ipynb)

from __code.math_images import MathImages

# * [mcp chips corrector](mcp_chips_corrector.ipynb)

from __code.mcp_chips_corrector.mcp_chips_corrector import McpChipsCorrector
from __code.mcp_chips_corrector.interface import Interface

# * [metadata ascii parser](metadata_ascii_parser.ipynb)

from __code.metadata_ascii_parser import *

# * [metadata overlapping images](metadata_overlapping_images.ipynb)

from __code.ipywe.myfileselector import FileSelection
from __code.metadata_overlapping_images.metadata_overlapping_images import MetadataOverlappingImagesUi

# * [normalization](normalization.ipynb)

from __code.normalization.normalization import *
from __code.roi_selection_ui import Interface

# * [normalization with simplify selection](normalization_with_simplify_selection.ipynb)

from __code.normalization.normalization_with_simplify_selection import NormalizationWithSimplifySelection

# * [outliers filtering](outliers_filtering_tool.ipynb)

from __code.outliers_filtering.main import Interface, InterfaceHandler

# * [overlay images](overlay_images.ipynb)

from __code.overlay_images.interface_handler import InterfaceHandler
from __code.overlay_images.overlay_images import OverlayImages

# * [panoramic stitching](panoramic_stitching.ipynb)

from __code.panoramic_stitching.panoramic_stitching import PanoramicStitching

# * [panoramic stitching for tof](panoramic_stitching_for_tof.ipynb)

from __code.panoramic_stitching_for_tof.panoramic_stitching_for_tof import PanoramicStitching

# * [bragg edge profile](bragg_edge_profile.ipynb)

from __code.bragg_edge.bragg_edge_normalization import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

# * [profile](profile.ipynb)

o_builder = UiBuilder(ui_name = 'ui_profile.ui')
from __code.ipywe.myfileselector import FileSelection
from __code.profile import ProfileUi

# * [radial profile](radial_profile.ipynb)

from __code.ipywe.myfileselector import FileSelection
from __code.radial_profile.radial_profile import RadialProfile, SelectRadialParameters

# * [water intake profile_calculator](water_intake_profile_calculator.ipynb)

o_builder = UiBuilder(ui_name = 'ui_water_intake_profile.ui')
from __code.roi_selection_ui import Interface
from __code.water_intake_profile_calculator import WaterIntakeProfileCalculator, WaterIntakeProfileSelector

# * [radial profile](radial_profile.ipynb)

from __code.radial_profile.radial_profile import RadialProfile, SelectRadialParameters

# * [registration](registration.ipynb)

from __code.registration.registration import RegistrationUi

# * [rename files](rename_files.ipynb)

from __code.rename_files.rename_files import NamingSchemaDefinition, FormatFileNameIndex

# * [resonance imaging experiment vs theory](resonance_imaging_experiment_vs_theory.ipynb)

# +
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_experiment_vs_theory.ui')
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_layers_input.ui')

from __code import file_handler, utilities
from __code.display_counts_of_region_vs_stack_vs_theory import ImageWindow
from __code.display_imaging_resonance_sample_definition import SampleWindow
from NeuNorm.normalization import Normalization
from __code.ipywe import fileselector
# -

# * [roi statistics for a stack of images](roi_statistics_vs_stack.ipynb)

from __code.roi_statistics_vs_stack.main import ImageWindow, FileHandler

# * [rotate and crop images](rotate_and_crop_images.ipynb)

o_builder = UiBuilder(ui_name = 'ui_rotate_and_crop.ui')
from __code.load_images import LoadImages
from __code.rotate_and_crop_images import RotateAndCropImages, Export

# * [scale overlapping images](scale_overlapping_images.ipynb)

o_builder = UiBuilder(ui_name = 'ui_scale_overlapping_images.ui')
from __code.ipywe.myfileselector import FileSelection

# * [sequential combine images using metadata](sequential_combine_images_using_metadata.ipynb)

from __code.sequential_combine_images_using_metadata import SequentialCombineImagesUsingMetadata

# * [shifting time offset](shifting_time_offset.ipynb)

from __code.select_files_and_folders import SelectFiles, SelectFolder
from __code.shifting_time_offset import ShiftTimeOffset

# * [water intake profile_calculator](water_intake_profile_calculator.ipynb)

o_builder = UiBuilder(ui_name = 'ui_water_intake_profile.ui')
from __code.water_intake_profile_calculator import WaterIntakeProfileCalculator, WaterIntakeProfileSelector

# * [wave front dynamics](wave_front_dynamics.ipynb)

from __code.wave_front_dynamics.wave_front_dynamics import WaveFrontDynamics, WaveFrontDynamicsUI


