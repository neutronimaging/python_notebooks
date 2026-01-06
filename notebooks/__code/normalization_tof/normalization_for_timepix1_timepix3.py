import argparse
import glob
import logging
import multiprocessing as mp
import os
from random import sample
import shutil
from pathlib import Path
from typing import Tuple

from annotated_types import Not
import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from PIL import Image
from skimage.io import imread
from scipy.ndimage import median_filter

from __code.normalization_tof.utilities import *

# from enum import Enum
# from scipy.constants import h, c, electron_volt, m_n
# from timepix_geometry_correction.correct import TimepixGeometryCorrection

MARKERSIZE = 2

class NormalizedData:
    data= {}
    lambda_array= None
    tof_array= None
    energy_array= None


from __code.normalization_tof.units import (
    DistanceUnitOptions,
    EnergyUnitOptions,
    TimeUnitOptions,
    convert_array_from_time_to_energy,
    convert_array_from_time_to_lambda,
)
# from __code.normalization_tof.normalization_for_timepix import create_master_dict

LOG_PATH = "/SNS/VENUS/shared/log/"
LOAD_DTYPE = np.uint16

PROTON_CHARGE_TOLERANCE = 0.1

def initialize_logging():
    """initialize logging"""
    file_name, ext = os.path.splitext(os.path.basename(__file__))
    user_name = os.getlogin()  # add user name to the log file name
    log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
    logging.basicConfig(filename=log_file_name,
                        filemode='w',
                        format='[%(levelname)s] - %(asctime)s - %(message)s',
                        level=logging.INFO)
    logging.info(f"*** Starting a new script {file_name} ***")


def normalization_with_list_of_full_path(
    sample_dict: dict = None,
    combine_samples: bool = False,
    ob_dict: dict = None,
    dc_dict: dict = None,
    spectra_array: np.ndarray = None,
    output_folder: str = "./",
    verbose: bool = False,
    proton_charge_flag=True,
    # monitor_counts_flag=False,
    # shutter_counts_flag=True,
    replace_ob_zeros_by_nan_flag=False,
    replace_ob_zeros_by_local_median_flag=False,
    kernel_size_for_local_median: Tuple[int, int, int] = (3, 3, 3),
    max_iterations: int = 10,
    output_tif: bool = True,
    instrument: str = "VENUS",
    detector_delay_us: float = None,
    preview: bool = False,
    distance_source_detector_m: float = 25,
    correct_chips_alignment_flag: bool = True,
    correct_chips_alignment_config: dict = None,
    export_mode: dict = None,
    roi = None,
    container_roi = None,
    container_roi_file = None) -> NormalizedData:
    """normalize the sample data with ob data using proton charge and shutter counts
    
    Args:
        sample_dict (dict): dictionary with sample run numbers and their data
            {base_name_run1: {'full_path': full_path, 'nexus': nexus_path},
             base_name_run2: {'full_path': full_path, 'nexus': nexus_path}, ...}

        ob_dict (dict): dictionary with ob run numbers and their data
            {base_name_run1: {'full_path': full_path, 'nexus': nexus_path},
             base_name_run2: {'full_path': full_path, 'nexus': nexus_path}, ...}

        dc_dict (dict): dictionary with dc run numbers and their data
            {base_name_run1: {'full_path': full_path, 'nexus': nexus_path},
             base_name_run2: {'full_path': full_path, 'nexus': nexus_path}, ...}

                     output_folder (str): folder to save the output data
        verbose (bool): if True, display additional information
        combine_samples (bool): if True, combine sample runs
        proton_charge_flag (bool): if True, normalize by proton charge
        monitor_counts_flag (bool): if True, normalize by monitor counts
        shutter_counts_flag (bool): if True, normalize by shutter counts
        replace_ob_zeros_by_nan_flag (bool): if True, replace OB zeros by NaN
        replace_ob_zeros_by_local_median_flag (bool): if True, replace OB zeros by local median
        kernel_size_for_local_median (Tuple[int, int, int]): kernel size for local median (y, x, tof)
        max_iterations (int): maximum number of iterations for local median
        output_tif (bool): if True, export the data as tif files
        instrument (str): instrument name
        detector_delay_us (float): detector delay in microseconds
        preview (bool): if True, display preview of the data
        distance_source_detector_m (float): distance from source to detector in meters
        correct_chips_alignment_flag (bool): if True, correct chips alignment
        correct_chips_alignment_config (dict): configuration for chips alignment correction
        export_mode (dict): dictionary with export options
        roi (Roi): region of interest for full spectrum normalization
        container_roi (Roi): region of interest for container only normalization 
        container_roi_file (str): file path to container ROI file (scitiff format) (will take precedence over container_roi if both are provided)

    Returns:
        normalized_data | np.ndarray: normalized data
    """

    initialize_logging()

    logging.info("=============== Starting normalization ===============")
    dict_to_return = NormalizedData()

    # list sample and ob run numbers
    logging.info(f"{sample_dict.keys() = }")
    if verbose:
        display(HTML(f"Sample run numbers: {list(sample_dict.keys())}"))

    logging.info(f"{ob_dict.keys() = }")
    if verbose:
        display(HTML(f"List of ob run numbers: {list(ob_dict.keys())}"))

    logging.info(f"{output_folder = }")

    export_corrected_stack_of_sample_data = export_mode.get("sample_stack", False)
    export_corrected_stack_of_ob_data = export_mode.get("ob_stack", False)
    export_corrected_stack_of_normalized_data = export_mode.get("normalized_stack", False)
    # export_corrected_stack_of_combined_normalized_data = export_mode.get("combined_normalized_stack", False)
    export_corrected_integrated_sample_data = export_mode.get("sample_integrated", False)
    export_corrected_integrated_ob_data = export_mode.get("ob_integrated", False)
    export_corrected_integrated_normalized_data = export_mode.get("normalized_integrated", False)
    # export_corrected_integrated_combined_normalized_data = export_mode.get("combined_normalized_integrated", False)

    export_x_axis = export_mode.get("x_axis", True)

    logging.info("Input parameters:")
    
    logging.info(f"\t{sample_dict = }")
    logging.info(f"\t{combine_samples =}")
    logging.info(f"\t{ob_dict = }")
    logging.info(f"\t{dc_dict = }")
    logging.info(f"{spectra_array = }")
    
    logging.info(f"")
    logging.info(f"- export mode:")
    logging.info(f"\t{export_corrected_stack_of_sample_data = }")
    logging.info(f"\t{export_corrected_stack_of_ob_data = }")
    logging.info(f"\t{export_corrected_stack_of_normalized_data = }")
    logging.info(f"\t{export_corrected_integrated_sample_data = }")
    logging.info(f"\t{export_corrected_integrated_ob_data = }")
    logging.info(f"\t{export_corrected_integrated_normalized_data = }")
    
    logging.info(f"")
    logging.info(f"{roi =}")
    logging.info(f"{export_x_axis = }")
    logging.info(f"{proton_charge_flag = }")
    logging.info(f"{replace_ob_zeros_by_nan_flag = }")
    logging.info(f"{replace_ob_zeros_by_local_median_flag = }")
    logging.info(f"{kernel_size_for_local_median = }")
    logging.info(f"{max_iterations = }")
    logging.info(f"{correct_chips_alignment_flag = }")
    logging.info(f"{distance_source_detector_m = }")
    logging.info(f"{detector_delay_us = }")
    logging.info(f"")
    
    sample_master_dict, sample_status_metadata = create_master_dict(
        data_dictionary=sample_dict, 
        data_type=DataType.sample, 
        instrument=instrument,
        spectra_array=spectra_array,
    )
    ob_master_dict, ob_status_metadata = create_master_dict(
        data_dictionary=ob_dict, 
        data_type=DataType.ob, 
        instrument=instrument,
        spectra_array=spectra_array,
    )

    dc_master_dict, dc_status_metadata = create_master_dict(
        data_dictionary=dc_dict, 
        data_type=DataType.dc, 
        instrument=instrument,
        spectra_array=spectra_array,
    )

    # load ob images ===============================
    load_images(master_dict=ob_master_dict, data_type=DataType.ob, verbose=verbose)
   
    if proton_charge_flag:
        normalized_by_proton_charge = (
            sample_status_metadata.all_proton_charge_found and ob_status_metadata.all_proton_charge_found
        )
    else:
        normalized_by_proton_charge = False
    logging.info(f"{normalized_by_proton_charge = }")

    # combine all ob images
    ob_data_combined, ob_sum_proton_charge = combine_images(
                                    data_type=DataType.ob,
                                    master_dict=ob_master_dict,
                                    use_proton_charge=normalized_by_proton_charge,
                                    replace_zeros_by_nan=replace_ob_zeros_by_nan_flag,
                                    replace_zeros_by_local_median=replace_ob_zeros_by_local_median_flag,
                                    kernel_size_for_local_median=kernel_size_for_local_median,
                                    max_iterations=max_iterations,
                                )
    logging.info(f"{ob_data_combined.shape = }")
    logging.info(f"{ob_sum_proton_charge = }")
    logging.info(f"number of NaN in ob_data_combined data: {np.sum(np.isnan(ob_data_combined))}")
    logging.info(f"number of inf in ob_data_combined data: {np.sum(np.isinf(ob_data_combined))}")
    logging.info(f"number of zeros in ob_data_combined data: {np.sum(ob_data_combined == 0)} ")

    if correct_chips_alignment_flag:
        correct_chips_alignment(ob_data_combined, 
                                correct_chips_alignment_config, 
                                verbose=verbose)

    ob_data_combined_for_spectrum = calculate_ob_data_combined_used_by_spectrum_normalization(roi=roi,
                                                                                 ob_data_combined=ob_data_combined,
                                                                                 verbose=verbose)

    # export ob data if requested
    first_ob_run_number = list(ob_master_dict.keys())[0]
    if export_corrected_stack_of_ob_data or export_corrected_integrated_ob_data:
        export_ob_images(
            ob_master_dict.keys(),
            output_folder,
            export_corrected_stack_of_ob_data,
            export_corrected_integrated_ob_data,
            ob_data_combined,
            spectra_file_name=ob_master_dict[first_ob_run_number][MasterDictKeys.spectra_file_name],
            spectra_array=spectra_array,
        )

    # load dc images ================================
    dc_master_dict = load_images(master_dict=dc_master_dict, data_type=DataType.dc, verbose=verbose)

    # combine all dc images
    dc_data_combined = combine_dc_images(dc_master_dict)
    
    if dc_data_combined is not None:
        
        if correct_chips_alignment_flag:
            dc_data_combined = correct_chips_alignment(dc_data_combined, 
                                                    correct_chips_alignment_config, 
                                                    verbose=verbose)

    if (dc_data_combined is not None) and (roi is not None):
        dc_data_combined_for_spectrum = [np.sum(np.sum(_data, axis=0), axis=0) for _data in dc_data_combined]
        logging.info(f"\t{np.shape(dc_data_combined) = }")
        logging.info(f"\t{np.shape(dc_data_combined_for_spectrum) = }")
        
        if correct_chips_alignment_flag:
            dc_data_combined_for_spectrum = correct_chips_alignment(dc_data_combined_for_spectrum, 
                                                    correct_chips_alignment_config, 
                                                    verbose=verbose)

    else:
        logging.info(f"\tno roi provided! Skipping the normalization of spectrum.")
        dc_data_combined_for_spectrum = None

    # load sample images ===============================
    load_images(master_dict=sample_master_dict, data_type=DataType.sample, verbose=verbose)
    if correct_chips_alignment_flag:
        correct_all_samples_chips_alignment(sample_master_dict, 
                                            correct_chips_alignment_config, 
                                            verbose=verbose)

    normalized_data = {}
    integrated_normalized_data = {}
    spectrum_normalized_data = {}

    if combine_samples:
        
        # combine all sample images and then perform normalization 
        sample_data_combined, sample_sum_proton_charge = combine_images(
                                    data_type=DataType.sample,
                                    master_dict=sample_master_dict,
                                    use_proton_charge=normalized_by_proton_charge,
                                    # use_monitor_counts=normalized_by_monitor_counts,
                                    replace_zeros_by_nan=False,
                                    replace_zeros_by_local_median=replace_ob_zeros_by_local_median_flag,
                                    kernel_size_for_local_median=kernel_size_for_local_median,
                                    max_iterations=max_iterations,
                                )

        logging.info("**********************************")
        list_run_number = list(sample_master_dict.keys())
        str_list_run_number = '_'.join([str(r) for r in list_run_number])
        logging.info(f"normalization of combined sample runs {list_run_number}")
        if verbose:
            display(HTML(f"Normalization of combined sample runs {list_run_number}"))
            
        # get statistics of sample data
        logging_statistics_of_data(data=sample_data_combined, data_type=DataType.sample_combined)
        
        if correct_chips_alignment_flag:
            sample_data_combined = correct_chips_alignment(sample_data_combined, 
                                    correct_chips_alignment_config, 
                                    verbose=verbose)
        
        if normalized_by_proton_charge:
            logging.info(f"Normalizing by proton charge")
            logging.info(f"\t{sample_sum_proton_charge = }")
            if verbose:
                display(HTML(f"Normalizing by proton charge"))
            sample_data_combined /= sample_sum_proton_charge 

        if (container_roi is not None) or (container_roi_file is not None):
                logging.info(f"Applying container normalization:")
                logging.info(f"\t {container_roi = }")
                logging.info(f"\t {container_roi_file = }")
                if verbose:
                    display(HTML(f"Applying container normalization:"))
                
                sample_data_combined, container_roi_file = normalize_by_container_roi(
                    sample_data=sample_data_combined,
                    container_roi=container_roi,
                    container_roi_file=container_roi_file,
                    output_folder=output_folder,
                    sample_run_number=str_list_run_number,
                )
                if verbose and (container_roi_file is not None):
                    display(HTML(f"Container roi file created: {container_roi_file}."))

        # export sample data after correction if requested
        if export_corrected_stack_of_sample_data or export_corrected_integrated_sample_data:
            export_sample_images(
                output_folder,
                export_corrected_stack_of_sample_data,
                export_corrected_integrated_sample_data,
                str_list_run_number,
                sample_data_combined,
                spectra_file_name=sample_master_dict[list_run_number[0]][MasterDictKeys.spectra_file_name],
                spectra_array=spectra_array,
            )

        _normalized_dict = perform_normalization(sample_data_combined, ob_data_combined, dc_data_combined)
        _normalized_data = _normalized_dict['normalized_data']
        _integrated_normalized_data = _normalized_dict['integrated_normalized_data']       
        integrated_normalized_data[str_list_run_number] = _integrated_normalized_data
        normalized_data[str_list_run_number] = _normalized_data

        _spectrum_normalized_data = perform_spectrum_normalization(roi=roi, 
                                                                sample_data=sample_data_combined, 
                                                                ob_data_combined_for_spectrum=ob_data_combined_for_spectrum, 
                                                                dc_data_combined=dc_data_combined,
                                                                dc_data_combined_for_spectrum=dc_data_combined_for_spectrum)
        spectrum_normalized_data[str_list_run_number] = _spectrum_normalized_data

        # normalized_data[_sample_run_number] = np.array(np.divide(_sample_data, ob_data_combined))
        logging.info(f"{normalized_data[str_list_run_number].shape = }")
        logging.info(f"{normalized_data[str_list_run_number].dtype = }")
        logging.info(f"number of NaN in normalized data: {np.sum(np.isnan(normalized_data[str_list_run_number]))}")
        logging.info(f"number of inf in normalized data: {np.sum(np.isinf(normalized_data[str_list_run_number]))}")

        if detector_delay_us is None:
            detector_delay_us = sample_master_dict[list_run_number[0]][MasterDictKeys.detector_delay_us]
            logging.info(f"detector_delay argument is None, using detector delay from first sample run: {detector_delay_us} us")
        
        time_spectra = sample_master_dict[list_run_number[0]][MasterDictKeys.list_spectra]

        dict_to_return.tof_array = time_spectra

        if time_spectra is None:
            logging.info("Time spectra is None, cannot convert to lambda or energy arrays")
            lambda_array = None
            energy_array = None
        
        else:

            logging.info(f"We have a time_spectra!")
            logging.info(f"time spectra shape: {time_spectra.shape}")
            
            if detector_delay_us is None:
                detector_delay_us = 0.0
                logging.info(f"detector delay is None, setting it to {detector_delay_us} us")

            logging.info(f"we have a detector delay of {detector_delay_us} us")

            lambda_array = convert_array_from_time_to_lambda(
                time_array=time_spectra,
                time_unit=TimeUnitOptions.s,
                distance_source_detector=distance_source_detector_m,
                distance_source_detector_unit=DistanceUnitOptions.m,
                detector_offset=detector_delay_us,
                detector_offset_unit=TimeUnitOptions.us,
                lambda_unit=DistanceUnitOptions.angstrom,
            )
            logging.info(f"Lambda array shape: {lambda_array.shape}")
            logging.info(f"{lambda_array = }")

            energy_array = convert_array_from_time_to_energy(
                time_array=time_spectra,
                time_unit=TimeUnitOptions.s,
                distance_source_detector=distance_source_detector_m,
                distance_source_detector_unit=DistanceUnitOptions.m,
                detector_offset=detector_delay_us,
                detector_offset_unit=TimeUnitOptions.us,
                energy_unit=EnergyUnitOptions.eV,
            )
            logging.info(f"Energy array shape: {energy_array.shape}")
            logging.info(f"{energy_array = }")

        dict_to_return.lambda_array = lambda_array
        dict_to_return.energy_array = energy_array

        logging.info(f"Preview: {preview = }")
        if preview:
            preview_normalized_data(sample_data_combined, 
                                    ob_data_combined, 
                                    dc_data_combined, 
                                    normalized_data, 
                                    lambda_array,
                                    energy_array, 
                                    detector_delay_us, 
                                    str_list_run_number,
                                    combine_samples,
                                    _spectrum_normalized_data,
                                    roi,
                                    )
            
        if export_corrected_integrated_normalized_data or export_corrected_stack_of_normalized_data:

            export_normalized_data(ob_master_dict=ob_master_dict, 
                sample_master_dict=sample_master_dict, 
                _sample_run_number=str_list_run_number,
                normalized_data=normalized_data, 
                integrated_normalized_data=integrated_normalized_data,
                _spectrum_normalized_data=_spectrum_normalized_data,
                lambda_array=lambda_array, 
                energy_array=energy_array, 
                output_folder=output_folder, 
                export_corrected_stack_of_normalized_data=export_corrected_stack_of_normalized_data,
                export_corrected_integrated_normalized_data=export_corrected_integrated_normalized_data,
                roi=roi,
                spectra_array=spectra_array,
                spectra_file=sample_master_dict[list_run_number[0]][MasterDictKeys.spectra_file_name])

    else:
    

        # normalize the sample data
        for _sample_run_number in sample_master_dict.keys():
            
            logging.info("**********************************")
            logging.info(f"normalization of run {_sample_run_number}")
            if verbose:
                display(HTML(f"Normalization of run {_sample_run_number}"))

            _sample_data = sample_master_dict[_sample_run_number][MasterDictKeys.data]

            # get statistics of sample data
            logging_statistics_of_data(data=_sample_data, data_type=DataType.sample)
      
            if correct_chips_alignment_flag:
                _sample_data = correct_chips_alignment(_sample_data, 
                                                       correct_chips_alignment_config, 
                                                       verbose=verbose)
      
            if normalized_by_proton_charge:
                if verbose:
                    display(HTML(f"Normalizing by proton charge"))
                _sample_data = normalize_by_proton_charge(sample_master_dict, 
                                                          _sample_run_number, 
                                                          _sample_data)

            if (container_roi is not None) or (container_roi_file is not None):
                logging.info(f"Applying container normalization:")
                logging.info(f"\t {container_roi = }")
                logging.info(f"\t {container_roi_file = }")
                if verbose:
                    display(HTML(f"Applying container normalization:"))
                
                _sample_data, container_roi_file = normalize_by_container_roi(
                    sample_data=_sample_data,
                    container_roi=container_roi,
                    container_roi_file=container_roi_file,
                    output_folder=output_folder,
                    sample_run_number=_sample_run_number,
                )
                if verbose and (container_roi_file is not None):
                    display(HTML(f"Container roi file created: {container_roi_file}."))

            logging.info(f"{_sample_data.shape = }")
            logging.info(f"{_sample_data.dtype = }")
            logging.info(f"{ob_data_combined.shape = }")
            logging.info(f"{ob_data_combined.dtype = }")

            # export sample data after correction if requested
            if export_corrected_stack_of_sample_data or export_corrected_integrated_sample_data:
                export_sample_images(
                    output_folder,
                    export_corrected_stack_of_sample_data,
                    export_corrected_integrated_sample_data,
                    _sample_run_number,
                    _sample_data,
                    spectra_file_name=sample_master_dict[_sample_run_number][MasterDictKeys.spectra_file_name],
                    spectra_array=spectra_array,
                )

            _normalized_dict = perform_normalization(_sample_data, ob_data_combined, dc_data_combined)
            _normalized_data = _normalized_dict['normalized_data']
            _integrated_normalized_data = _normalized_dict['integrated_normalized_data']       
            integrated_normalized_data[_sample_run_number] = _integrated_normalized_data
            normalized_data[_sample_run_number] = _normalized_data

            _spectrum_normalized_data = perform_spectrum_normalization(roi=roi, 
                                                                    sample_data=_sample_data, 
                                                                    ob_data_combined_for_spectrum=ob_data_combined_for_spectrum, 
                                                                    dc_data_combined=dc_data_combined,
                                                                    dc_data_combined_for_spectrum=dc_data_combined_for_spectrum)
            spectrum_normalized_data[_sample_run_number] = _spectrum_normalized_data

            # normalized_data[_sample_run_number] = np.array(np.divide(_sample_data, ob_data_combined))
            logging.info(f"{normalized_data[_sample_run_number].shape = }")
            logging.info(f"{normalized_data[_sample_run_number].dtype = }")
            logging.info(f"number of NaN in normalized data: {np.sum(np.isnan(normalized_data[_sample_run_number]))}")
            logging.info(f"number of inf in normalized data: {np.sum(np.isinf(normalized_data[_sample_run_number]))}")

            if detector_delay_us is None:
                detector_delay_us = sample_master_dict[_sample_run_number][MasterDictKeys.detector_delay_us]
                logging.info(f"detector_delay argument is None, using detector delay from sample run {_sample_run_number}: {detector_delay_us} us")
                
            time_spectra = sample_master_dict[_sample_run_number][MasterDictKeys.list_spectra]

            dict_to_return.tof_array = time_spectra

            if time_spectra is None:
                logging.info("Time spectra is None, cannot convert to lambda or energy arrays")
                lambda_array = None
                energy_array = None
            
            else:

                logging.info(f"We have a time_spectra!")
                logging.info(f"time spectra shape: {time_spectra.shape}")
                
                if detector_delay_us is None:
                    detector_delay_us = 0.0
                    logging.info(f"detector delay is None, setting it to {detector_delay_us} us")

                logging.info(f"we have a detector delay of {detector_delay_us} us")

                lambda_array = convert_array_from_time_to_lambda(
                    time_array=time_spectra,
                    time_unit=TimeUnitOptions.s,
                    distance_source_detector=distance_source_detector_m,
                    distance_source_detector_unit=DistanceUnitOptions.m,
                    detector_offset=detector_delay_us,
                    detector_offset_unit=TimeUnitOptions.us,
                    lambda_unit=DistanceUnitOptions.angstrom,
                )
                logging.info(f"Lambda array shape: {lambda_array.shape}")
                logging.info(f"{lambda_array = }")

                energy_array = convert_array_from_time_to_energy(
                    time_array=time_spectra,
                    time_unit=TimeUnitOptions.s,
                    distance_source_detector=distance_source_detector_m,
                    distance_source_detector_unit=DistanceUnitOptions.m,
                    detector_offset=detector_delay_us,
                    detector_offset_unit=TimeUnitOptions.us,
                    energy_unit=EnergyUnitOptions.eV,
                )
                logging.info(f"Energy array shape: {energy_array.shape}")
                logging.info(f"{energy_array = }")

            dict_to_return.lambda_array = lambda_array
            dict_to_return.energy_array = energy_array

            logging.info(f"Preview: {preview = }")
            if preview:
                preview_normalized_data(_sample_data, 
                                        ob_data_combined, 
                                        dc_data_combined, 
                                        normalized_data, 
                                        lambda_array,
                                        energy_array, 
                                        detector_delay_us, 
                                        _sample_run_number,
                                        combine_samples,
                                        _spectrum_normalized_data,
                                        roi,
                                        )
                
            if export_corrected_integrated_normalized_data or export_corrected_stack_of_normalized_data:

                export_normalized_data(ob_master_dict=ob_master_dict, 
                    sample_master_dict=sample_master_dict, 
                    _sample_run_number=_sample_run_number,
                    normalized_data=normalized_data, 
                    integrated_normalized_data=integrated_normalized_data,
                    _spectrum_normalized_data=_spectrum_normalized_data,
                    lambda_array=lambda_array, 
                    energy_array=energy_array, 
                    output_folder=output_folder, 
                    export_corrected_stack_of_normalized_data=export_corrected_stack_of_normalized_data,
                    export_corrected_integrated_normalized_data=export_corrected_integrated_normalized_data,
                    roi=roi,
                    spectra_array=spectra_array,
                    spectra_file=sample_master_dict[_sample_run_number][MasterDictKeys.spectra_file_name])
          
    # if combine_samples:

    #     # combine all normalized data
    #     array_of_normalized_data = []
    #     for _key in normalized_data.keys():
    #         array_of_normalized_data.append(normalized_data[_key])

    #     combined_normalized_data = np.nanmean(np.array(array_of_normalized_data), axis=0)
    #     combined_spectrum_normalized_data = np.nanmean(np.array(list(spectrum_normalized_data.values())), axis=0)
    #     dict_to_return.data['combined'] = combined_normalized_data

    #     # if preview, display the combined normalized data
    #     if preview:
            
    #         fig, axs3 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    #         normalized_data_integrated = np.nanmean(combined_normalized_data, axis=0)
    #         im2 = axs3[0].imshow(normalized_data_integrated, cmap="gray")
    #         plt.colorbar(im2, ax=axs3[0])
    #         axs3[0].set_title(f"Integrated combined Normalized data")

    #         _label = "pixel by pixel normalization profile of full image"
    #         if roi is not None:
    #             profile_step1 = np.nanmean(combined_normalized_data[:, roi.top:roi.top+roi.height, roi.left:roi.left+roi.width], axis=1)
    #             profile = np.nanmean(profile_step1, axis=1)
    #         else:
    #             profile_step1 = np.nanmean(combined_normalized_data, axis=1)
    #             profile = np.nanmean(profile_step1, axis=1)
        
    #         axs3[1].plot(profile, 'o', markersize=MARKERSIZE, label=_label)
    #         axs3[1].set_xlabel("File image index")
    #         axs3[1].set_ylabel("Transmission (a.u.)")
    #         axs3[1].legend()

    #         plt.tight_layout()

    #         if lambda_array is not None:

    #             fig, axs4 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    #             logging.info(f"{np.shape(profile) = }")

    #             axs4[0].plot(lambda_array, profile, "*", markersize=MARKERSIZE, label=_label)
    #             #axs4[0].plot(lambda_array, combined_spectrum_normalized_data, label="spectrum normalization")
    #             axs4[0].set_xlabel("Lambda (A)")
    #             axs4[0].set_ylabel("mean of full image")
    #             axs4[0].legend()

    #             axs4[1].plot(energy_array, profile, "*", markersize=MARKERSIZE, label=_label)
    #             #axs4[1].plot(energy_array, combined_spectrum_normalized_data, label="spectrum normalization")
    #             axs4[1].set_xlabel("Energy (eV)")
    #             axs4[1].set_ylabel("Transmission (a.u.)")
    #             axs4[1].set_xscale("log")
    #             axs4[1].legend()

    #             plt.tight_layout()

    #             if combined_spectrum_normalized_data is not None:
    #                 fig, axs5 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    #                 logging.info(f"{np.shape(profile) = }")

    #                 axs5[0].plot(lambda_array, combined_spectrum_normalized_data, "r*", 
    #                              markersize=MARKERSIZE, 
    #                              label="spectrum normalization of ROI")
    #                 axs5[0].set_xlabel("Lambda (A)")
    #                 axs5[0].set_ylabel("mean of full image")
    #                 axs5[0].legend()

    #                 axs5[1].plot(energy_array, combined_spectrum_normalized_data, "r*",
    #                               markersize=MARKERSIZE, 
    #                               label="spectrum normalization of ROI")
    #                 axs5[1].set_xlabel("Energy (eV)")
    #                 axs5[1].set_ylabel("Transmission (a.u.)")
    #                 axs5[1].set_xscale("log")
    #                 axs5[1].legend()

    #                 plt.tight_layout()

    #     if export_corrected_integrated_combined_normalized_data or export_corrected_stack_of_combined_normalized_data:

    #         export_corrected_normalized_data(sample_master_dict=sample_master_dict,
    #                                   ob_master_dict=ob_master_dict,
    #                                   dc_master_dict=dc_master_dict,
    #                                    combined_normalized_data=combined_normalized_data,
    #                                    export_corrected_integrated_combined_normalized_data=export_corrected_integrated_combined_normalized_data,
    #                                    export_corrected_stack_of_combined_normalized_data=export_corrected_stack_of_combined_normalized_data,
    #                                    lambda_array=lambda_array,
    #                                    energy_array=energy_array,
    #                                    output_folder=output_folder, 
    #                                    spectra_array=spectra_array)
            
    # else:
    #     dict_to_return.data = normalized_data

    dict_to_return.data = normalized_data

    logging.info("Normalization and export is done!")
    if verbose:
        display(HTML("Normalization and export is done!"))

    return dict_to_return

