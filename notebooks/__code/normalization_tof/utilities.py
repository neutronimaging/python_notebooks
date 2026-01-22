import argparse
import glob
import logging
import multiprocessing as mp
import os
import shutil
from pathlib import Path
from sqlite3 import Time
from typing import Tuple

import h5py
from matplotlib import container
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
from PIL import Image
from skimage.io import imread
from scipy.ndimage import median_filter

from timepix_geometry_correction.correct import TimepixGeometryCorrection

from __code.normalization_tof import Roi
from __code._utilities.json import load_json, save_json

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

LOAD_DTYPE = np.uint16

PROTON_CHARGE_TOLERANCE = 0.1


class PLOT_SIZE:
    width = 8
    height = 5


SPECTRA_FILE_PREFIX = "Spectra.txt"

class DataType:
    sample = "sample"
    ob = "ob"
    dc = "dc"
    unknown = "unknown"
    sample_combined = "sample_combined"


class MasterDictKeys:
    frame_number = "frame_number"
    run_number = "run_number"
    proton_charge = "proton_charge"
    monitor_counts = "monitor_counts"
    matching_ob = "matching_ob"
    list_tif = "list_tif"
    data = "data"
    nexus_path = "nexus_path"
    data_path = "data_path"
    shutter_counts = "shutter_counts"
    list_spectra = "list_spectra"
    spectra_file_name = "spectra_file_name"
    detector_delay_us = "detector_delay_us"


class StatusMetadata:
    all_shutter_counts_found = True
    all_monitor_counts_found = True
    all_spectra_found = True
    all_proton_charge_found = True


def _worker(fl):
#    return (imread(fl).astype(LOAD_DTYPE)).swapaxes(0, 1)
    return (imread(fl).astype(np.float32)).swapaxes(0, 1)
    #return (imread(fl).astype(np.float32))


def load_data_using_multithreading(list_tif: list = None, combine_tof: bool = False) -> np.ndarray:
    """load data using multithreading"""
    with mp.Pool(processes=40) as pool:
        data = pool.map(_worker, list_tif)

    if combine_tof:
        return np.array(data).sum(axis=0)
    else:
        return np.array(data, dtype=np.float32)


def retrieve_list_of_tif(folder: str) -> list:
    """retrieve list of tif files in the folder"""
    list_tif = glob.glob(os.path.join(folder, "*.tif*"))
    list_tif.sort()
    return list_tif


def create_x_axis_file(
    lambda_array: np.ndarray = None, energy_array: np.ndarray = None, output_folder: str = "./"
) -> str:
    """create x axis file with lambda, energy and tof arrays"""
    x_axis_data = {
        "file_index": np.arange(len(lambda_array)),
        "lambda (Angstroms)": lambda_array,
        "energy (eV)": energy_array,
    }
    x_axis_file_name = os.path.join(output_folder, "x_axis.txt")
    pd_dataframe = pd.DataFrame(x_axis_data)
    pd_dataframe.to_csv(x_axis_file_name, index=False, sep=",")

    logging.info(f"X axis file created: {x_axis_file_name}")


def load_images(master_dict=None, data_type=DataType.sample, verbose=False):

    logging.info(f"Loading {data_type} data ...")
    for _run_number in master_dict.keys():
        logging.info(f"\tloading {data_type}# {_run_number} ... ")
        if verbose:
            display(HTML(f"Loading {data_type}# {_run_number} ..."))
        master_dict[_run_number][MasterDictKeys.data] = load_data_using_multithreading(
            master_dict[_run_number][MasterDictKeys.list_tif], combine_tof=False
        )
        logging.info(f"\t{data_type}# {_run_number} loaded!")
        logging.info(f"\t{master_dict[_run_number][MasterDictKeys.data].shape = }")
        if verbose:
            display(HTML(f"{data_type}# {_run_number} loaded!"))
            display(HTML(f"{master_dict[_run_number][MasterDictKeys.data].shape = }"))


def  calculate_ob_data_combined_used_by_spectrum_normalization(roi=None, ob_data_combined=None, verbose=False):

    logging.info(f"Calculating the ob_data_combined for spectrum normalization")
    if roi is not None:
        logging.info(f"\t{roi =}")
        x0 = roi.left
        y0 = roi.top
        width = roi.width
        height = roi.height
        ob_data_combined_for_spectrum = [np.sum(np.sum(_data[y0:y0 + height, x0:x0 + width], axis=0), axis=0) for _data in ob_data_combined]
        logging.info(f"\t{np.shape(ob_data_combined_for_spectrum) = }")
        logging.info(f"\t{np.shape(ob_data_combined) = }")

    else:
        logging.info(f"\tno roi provided! Skipping the normalization of spectrum.")
        ob_data_combined_for_spectrum = None

    if verbose:
        display(HTML(f"{ob_data_combined.shape = }"))

    return ob_data_combined_for_spectrum


def correct_chips_alignment(data_combined=None, correct_chips_alignment_config=None, verbose=False):
    """
    correct the chips position (fill the gaps between the chips) using the dedicated library
    timepix_geometry_correction (https://github.com/ornlneutronimaging/timepix_geometry_correction)

    Args:
        data (np.ndarray): input data array
        config (dict): configuration dictionary for chips alignment
    Returns:
        np.ndarray: corrected data array
    """
    logging.info("Correcting chips alignment ...")
    if verbose:
        display(HTML("Correcting chips alignment ..."))

    logging.info(f"\t{data_combined.shape = }")

    data_combined_corrected = np.zeros_like(data_combined)
    for _index, _data in enumerate(data_combined):
        o_corrector = TimepixGeometryCorrection(raw_images=_data,
                                                config=correct_chips_alignment_config)
        data_corrected = o_corrector.correct()
    
        # remove useless dimension
        data = np.array([np.squeeze(_data) for _data in data_corrected])
        data_combined_corrected_squeezed = np.squeeze(data)
        
        data_combined_corrected[_index] = data_combined_corrected_squeezed

    logging.info(f"\t{data_combined_corrected.shape = }")
    
    logging.info("Chips alignment corrected!")
    
    if verbose:
        display(HTML("Chips alignment corrected!"))
  
    return data_combined_corrected


def correct_all_samples_chips_alignment(sample_master_dict=None, correct_chips_alignment_config=None, verbose=False):
    for _sample_run_number in sample_master_dict.keys():
        sample_master_dict[_sample_run_number][MasterDictKeys.data] = correct_chips_alignment(
            sample_master_dict[_sample_run_number][MasterDictKeys.data], 
            correct_chips_alignment_config,
            verbose=verbose
        )


def normalize_by_proton_charge(master_dict=None, run_number=None, data=None):
    if master_dict is not None and run_number is not None:
        logging.info("\t -> Normalized by proton charge")
        proton_charge = master_dict[run_number][MasterDictKeys.proton_charge]
        logging.info(f"\t\t proton charge: {proton_charge} C")
        logging.info(f"\t\t{type(proton_charge) = }")
        logging.info(f"\t\tbefore division: {data.dtype = }")
        data = data / proton_charge
        logging.info(f"\t\tafter division: {data.dtype = }")
        return data


def normalize_by_monitor_counts(master_dict=None, run_number=None, data=None):
    logging.info("\t -> Normalized by monitor counts")
    monitor_counts = master_dict[run_number][MasterDictKeys.monitor_counts]
    logging.info(f"\t\t monitor counts: {monitor_counts}")
    logging.info(f"\t\t{type(monitor_counts) = }")
    data = data / monitor_counts
    logging.info(f"{data.shape = }")
    return data



def preview_normalized_data(_sample_data, ob_data_combined, dc_data_combined, 
                            normalized_data, 
                            lambda_array, energy_array, 
                            detector_delay_us, _sample_run_number,
                            combine_samples=False,
                            _spectrum_normalized_data=None,
                            roi=None):
   
    """preview normalized data"""

    # display preview of normalized data
    fig, axs1 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    sample_data_integrated = np.nanmean(_sample_data, axis=0)
    im0 = axs1[0].imshow(sample_data_integrated, cmap="gray")
    plt.colorbar(im0, ax=axs1[0])

    display(HTML(f"<h3>Preview of run {_sample_run_number}</h3>"))
    display(HTML(f"detector delay: {detector_delay_us:.2f} us"))
    
    axs1[0].set_title(f"Integrated Sample data")

    sample_integrated1 = np.nansum(_sample_data, axis=1)
    sample_integrated = np.nansum(sample_integrated1, axis=1)
    axs1[1].plot(sample_integrated, 'o')
    axs1[1].set_xlabel("File image index")
    axs1[1].set_ylabel("Transmission (a.u.)")
    plt.tight_layout()

    fig, axs2 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    ob_data_integrated = np.nanmean(ob_data_combined, axis=0)
    im1 = axs2[0].imshow(ob_data_integrated, cmap="gray")
    plt.colorbar(im1, ax=axs2[0])
    axs2[0].set_title("OB integrated data ")

    ob_integrated1 = np.nansum(ob_data_combined, axis=1)
    ob_integrated = np.nansum(ob_integrated1, axis=1)
    axs2[1].plot(ob_integrated, 'o')
    axs2[1].set_xlabel("File image index")
    axs2[1].set_ylabel("Transmission (a.u.)")
    plt.tight_layout()

    if dc_data_combined is not None:
        fig, axs_dc = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
        dc_data_integrated = np.nanmean(dc_data_combined, axis=0)
        im_dc = axs_dc[0].imshow(dc_data_integrated, cmap="gray")
        plt.colorbar(im_dc, ax=axs_dc[0])
        axs_dc[0].set_title("DC integrated data ")

        dc_integrated1 = np.nansum(dc_data_combined, axis=1)
        dc_integrated = np.nansum(dc_integrated1, axis=1)
        axs_dc[1].plot(dc_integrated, 'o')
        axs_dc[1].set_xlabel("File image index")
        axs_dc[1].set_ylabel("Transmission (a.u.)")
        plt.tight_layout()

    # if not combine_samples:
    fig, axs3 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
    normalized_data_integrated = np.nanmean(normalized_data[_sample_run_number], axis=0)
    im2 = axs3[0].imshow(normalized_data_integrated, cmap="gray", vmin=0, vmax=1)
    plt.colorbar(im2, ax=axs3[0])
    axs3[0].set_title(f"Integrated Normalized data")

    if roi is not None:
        x0 = roi.left
        y0 = roi.top
        width = roi.width
        height = roi.height
        axs3[0].add_patch(plt.Rectangle((x0, y0), width, height, fill=False, color="red", lw=2))

        profile_step1 = np.nanmean(normalized_data[_sample_run_number][:, y0:y0+height, x0:x0+width], axis=1)
        profile = np.nanmean(profile_step1, axis=1)
        _label = "pixel by pixel normalization profile of ROI"

    else:
        profile_step1 = np.nanmean(normalized_data[_sample_run_number], axis=1)
        profile = np.nanmean(profile_step1, axis=1)
        _label = "pixel by pixel normalization profile of full image"

    axs3[1].plot(profile, 'o', label=_label)
    axs3[1].set_xlabel("File image index")
    axs3[1].set_ylabel("Transmission (a.u.)")
    axs3[1].legend()
    plt.tight_layout()

    if lambda_array is not None:
        fig, axs4 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
        logging.info(f"{np.shape(profile) = }")

        axs4[0].plot(lambda_array, profile, "*", label=_label)
        axs4[0].set_xlabel("Lambda (A)")
        axs4[0].set_ylabel("Transmission (a.u.)")
        axs4[0].legend()

        axs4[1].plot(energy_array, profile, "*", label=_label)
        axs4[1].set_xlabel("Energy (eV)")
        axs4[1].set_ylabel("Transmission (a.u.)")
        axs4[1].set_xscale("log")
        axs4[1].legend()

        plt.tight_layout()

        if _spectrum_normalized_data is not None:

            fig, axs6 = plt.subplots(1, 2, figsize=(2 * PLOT_SIZE.width, PLOT_SIZE.height))
            logging.info(f"{np.shape(profile) = }")

            axs6[0].plot(lambda_array, _spectrum_normalized_data, "r*", 
                            markersize=MARKERSIZE, 
                            label="spectrum normalization of ROI")
            axs6[0].set_xlabel("Lambda (A)")
            axs6[0].set_ylabel("Transmission (a.u.)")
            axs6[0].legend()
            logging.info(f"{lambda_array = }")

            axs6[1].plot(energy_array, _spectrum_normalized_data, "r*", 
                            markersize=MARKERSIZE, 
                            label="spectrum normalization of ROI")
            axs6[1].set_xlabel("Energy (eV)")
            axs6[1].set_ylabel("Transmission (a.u.)")
            axs6[1].set_xscale("log")
            axs6[1].legend()
            logging.info(f"{energy_array = }")

            plt.tight_layout()

    plt.show()

def get_detector_offset_from_nexus(nexus_path: str) -> float:
    """get the detector offset from the nexus file"""
    with h5py.File(nexus_path, "r") as hdf5_data:
        try:
            detector_offset_micros = hdf5_data["entry"]["DASlogs"]["BL10:Det:TH:DSPT1:TIDelay"]["value"][0]
            # detector_offset_micros = hdf5_data["entry"]["DASlogs"]["BL10:Det:DSP1:Trig2:Delay"]["value"][0]
        except KeyError:
            detector_offset_micros = None
    return detector_offset_micros


def get_run_number_from_nexus(nexus_path: str) -> int:
    """get the run number from the nexus file"""
    with h5py.File(nexus_path, "r") as hdf5_data:
        try:
            run_number = hdf5_data["entry"]["entry_identifier"][:][0].decode("utf8")
        except KeyError:
            run_number = None
    return run_number

def export_sample_images(
    output_folder,
    export_corrected_stack_of_sample_data,
    export_corrected_integrated_sample_data,
    _sample_run_number,
    _sample_data,
    spectra_file_name=None,
    spectra_array=None
):
    logging.info(f"> Exporting sample corrected images to {output_folder} ...")

    logging.info(f"\t{_sample_run_number = }")
    logging.info(f"\t{spectra_file_name = }")
    logging.info(f"\t{spectra_array = }")

    sample_output_folder = os.path.join(output_folder, f"sample_{_sample_run_number}")
    os.makedirs(sample_output_folder, exist_ok=True)

    if export_corrected_stack_of_sample_data:
        output_stack_folder = os.path.join(sample_output_folder, "stack")
        logging.info(f"\tmaking folder {output_stack_folder}")
        os.makedirs(output_stack_folder, exist_ok=True)

        for _index, _data in enumerate(_sample_data):
            _output_file = os.path.join(output_stack_folder, f"image{_index:04d}.tif")
            make_tiff(data=_data, filename=_output_file)
        logging.info(f"\t -> Exporting sample data to {output_stack_folder} is done!")

        if spectra_array is not None:
            # manually create the file for spectra
            spectra_file_name = os.path.join(output_stack_folder, f"manually_created_{SPECTRA_FILE_PREFIX}")
            _full_counts_array = np.empty_like(spectra_array)
            for _index, _data in enumerate(_sample_data):
                _full_counts_array[_index] = np.nansum(_data)
            pd_spectra = pd.DataFrame({
                "shutter_time": spectra_array,
                "counts": _full_counts_array
            })
            pd_spectra.to_csv(spectra_file_name, index=False, sep=",")
            logging.info(f"\t -> Exporting manually created spectra file to {spectra_file_name} is done!")

        else:
            shutil.copy(spectra_file_name, os.path.join(output_stack_folder))
            logging.info(f"\t -> Exporting spectra file {spectra_file_name} to {output_stack_folder} is done!")
        
        display(HTML(f"Created folder {output_stack_folder} for sample outputs!"))
    
    if export_corrected_integrated_sample_data:
        # making up the integrated sample data
        sample_data_integrated = np.nanmean(_sample_data, axis=0)
        full_file_name = os.path.join(sample_output_folder, "integrated.tif")
        logging.info(f"\t -> Exporting integrated sample data to {full_file_name} ...")
        make_tiff(data=sample_data_integrated, filename=full_file_name)
        logging.info(f"\t -> Exporting integrated sample data to {full_file_name} is done!")


def export_ob_images(
    ob_run_numbers,
    output_folder,
    export_corrected_stack_of_ob_data,
    export_corrected_integrated_ob_data,
    ob_data_combined,
    spectra_file_name=None,
    spectra_array=None,
):
    """export ob images to the output folder"""
    logging.info(f"> Exporting combined ob images to {output_folder} ...")
    logging.info(f"\t{ob_run_numbers = }")
    list_ob_runs_number_only = [
        str(isolate_run_number_from_full_path(_ob_run_number)) for _ob_run_number in ob_run_numbers
    ]
    if len(list_ob_runs_number_only) == 1:
        ob_output_folder = os.path.join(output_folder, f"ob_{list_ob_runs_number_only[0]}")
    else:
        str_list_ob_runs = "_".join(list_ob_runs_number_only)
        ob_output_folder = os.path.join(output_folder, f"ob_{str_list_ob_runs}")
    os.makedirs(ob_output_folder, exist_ok=True)

    output_stack_folder = ""
    if export_corrected_stack_of_ob_data:
        output_stack_folder = os.path.join(ob_output_folder, "stack")
        logging.info(f"\tmaking folder {output_stack_folder}")
        os.makedirs(output_stack_folder, exist_ok=True)

    if export_corrected_integrated_ob_data:
        # making up the integrated ob data
        ob_data_integrated = np.nanmean(ob_data_combined, axis=0)
        full_file_name = os.path.join(ob_output_folder, "integrated.tif")
        logging.info(f"\t -> Exporting integrated ob data to {full_file_name} ...")
        make_tiff(data=ob_data_integrated, filename=full_file_name)
        logging.info(f"\t -> Exporting integrated ob data to {full_file_name} is done!")

    if export_corrected_stack_of_ob_data:
        logging.info(f"\t -> Exporting ob data to {output_stack_folder} ...")
        _list_data = ob_data_combined
        for _index, _data in enumerate(_list_data):
            _output_file = os.path.join(output_stack_folder, f"image{_index:04d}.tif")
            make_tiff(data=_data, filename=_output_file)
        logging.info(f"\t -> Exporting ob data to {output_stack_folder} is done!")
        
        if spectra_array is not None:
            # manually create the file for spectra
            spectra_file_name = os.path.join(output_stack_folder, f"manually_created_{SPECTRA_FILE_PREFIX}")
            _full_counts_array = np.empty_like(spectra_array)
            for _index, _data in enumerate(ob_data_combined):
                _full_counts_array[_index] = np.nansum(_data)
            pd_spectra = pd.DataFrame({
                "shutter_time": spectra_array,
                "counts": _full_counts_array
            })
            pd_spectra.to_csv(spectra_file_name, index=False, sep=",")
            logging.info(f"\t -> Exporting manually created spectra file to {spectra_file_name} is done!")

        else:
            # copy spectra file to the output folder
            shutil.copy(spectra_file_name, os.path.join(output_stack_folder))
            logging.info(f"\t -> Exported spectra file {spectra_file_name} to {output_stack_folder}!")

    display(HTML(f"Created folder {output_stack_folder} for OB outputs!"))


# def normalization(sample_folder=None, ob_folder=None, output_folder="./", verbose=False):
#     pass


def make_tiff(data: list, filename: str = "", metadata: dict = None) -> None:
    new_image = Image.fromarray(np.array(data), mode="F")
    if metadata:
        new_image.save(filename, tiffinfo=metadata)
    else:
        new_image.save(filename)


def isolate_run_number_from_full_path(run_number_full_path: str) -> str:
    """isolate the run number from the full path"""
    run_number = os.path.basename(run_number_full_path)
    return isolate_run_number(run_number)


def isolate_run_number(run_number_full_path: str) -> int:
    run_number = os.path.basename(run_number_full_path)
    # fixme needs to treat old data set and new data set
    # retrieve run number behind the string _Run_ in the file name
    split_1 = run_number.split("Run_")
    if len(split_1) == 2:
        run_number = split_1[1]
    else:
        split_2 = split_1[1].split("_")
        run_number = split_2[0]
    return int(run_number)


def init_master_dict(data_dictionary: dict) -> dict:
    master_dict = {}

    for _base_name in data_dictionary.keys():
        master_dict[_base_name] = {
            MasterDictKeys.nexus_path: data_dictionary[_base_name]["nexus"],
            MasterDictKeys.run_number: None,
            MasterDictKeys.frame_number: None,
            MasterDictKeys.data_path: data_dictionary[_base_name]["full_path"],
            MasterDictKeys.proton_charge: None,
            MasterDictKeys.matching_ob: [],
            MasterDictKeys.list_tif: [],
            MasterDictKeys.list_spectra: None,
            MasterDictKeys.spectra_file_name: None,
            MasterDictKeys.detector_delay_us: None,
            MasterDictKeys.data: None,
        }

    return master_dict


def retrieve_root_nexus_full_path(sample_folder: str) -> str:
    """retrieve the root nexus path from the sample folder"""
    clean_path = os.path.abspath(sample_folder)
    if clean_path[0] == "/":
        clean_path = clean_path[1:]

    path_splitted = clean_path.split("/")
    facility = path_splitted[0]
    instrument = path_splitted[1]
    ipts = path_splitted[2]

    return f"/{facility}/{instrument}/{ipts}/nexus/"


def update_dict_with_shutter_counts(master_dict: dict) -> tuple[dict, bool]:
    """update the master dict with shutter counts from shutter count file"""
    status_all_shutter_counts_found = True
    for run_number in master_dict.keys():
        data_path = master_dict[run_number][MasterDictKeys.data_path]
        _list_files = glob.glob(os.path.join(data_path, "*_ShutterCount.txt"))
        if len(_list_files) == 0:
            logging.info(f"Shutter count file not found for run {run_number}!")
            master_dict[run_number][MasterDictKeys.shutter_counts] = None
            status_all_shutter_counts_found
            continue
        else:
            shutter_count_file = _list_files[0]
            with open(shutter_count_file) as f:
                lines = f.readlines()
                list_shutter_counts = []
                for _line in lines:
                    _, _value = _line.strip().split("\t")
                    if _value == "0":
                        break
                    list_shutter_counts.append(float(_value))
                master_dict[run_number][MasterDictKeys.shutter_counts] = list_shutter_counts
    
    return master_dict, status_all_shutter_counts_found


def update_dict_with_spectra_files(master_dict: dict, spectra_array: np.ndarray = None) -> tuple[dict, bool]:
    """update the master dict with spectra values from spectra file"""
    status_all_spectra_found = True
    for _run_number in master_dict.keys():

        if spectra_array is not None:
            master_dict[_run_number][MasterDictKeys.list_spectra] = spectra_array
            master_dict[_run_number][MasterDictKeys.spectra_file_name] = "Provided array"

        else: 

            data_path = master_dict[_run_number][MasterDictKeys.data_path]
            _list_files = glob.glob(os.path.join(data_path, f"*_{SPECTRA_FILE_PREFIX}"))
            
            if len(_list_files) == 0:
                logging.info(f"Spectra file not found for run {_run_number}!")
                master_dict[_run_number][MasterDictKeys.list_spectra] = None
                status_all_spectra_found = False
                continue
            
            else:
                spectra_file = _list_files[0]
                master_dict[_run_number][MasterDictKeys.spectra_file_name] = spectra_file
                pd_spectra = pd.read_csv(spectra_file, sep=",", header=0)
                shutter_time = pd_spectra["shutter_time"].values
                master_dict[_run_number][MasterDictKeys.list_spectra] = shutter_time

    return master_dict, status_all_spectra_found


def update_dict_with_proton_charge(master_dict: dict) -> tuple[dict, bool]:
    """update the master dict with proton charge from nexus file"""
    status_all_proton_charge_found = True
    for _run_number in master_dict.keys():
        _nexus_path = master_dict[_run_number][MasterDictKeys.nexus_path]
        if _nexus_path is None or not os.path.exists(_nexus_path):
            logging.info(f"Nexus file not found for run {_run_number}!")
            master_dict[_run_number][MasterDictKeys.proton_charge] = None
            status_all_proton_charge_found = False
            continue

        try:
            with h5py.File(_nexus_path, "r") as hdf5_data:
                proton_charge = hdf5_data["entry"][MasterDictKeys.proton_charge][0] / 1e12
        except KeyError:
            proton_charge = None
            status_all_proton_charge_found = False
        master_dict[_run_number][MasterDictKeys.proton_charge] = np.float32(proton_charge)
    return status_all_proton_charge_found


def update_dict_with_monitor_counts(master_dict: dict) -> bool:
    """update the master dict with monitor counts from nexus file"""
    status_all_monitor_counts_found = True
    for _run_number in master_dict.keys():
        _nexus_path = master_dict[_run_number][MasterDictKeys.nexus_path]
        if _nexus_path is None or not os.path.exists(_nexus_path):
            logging.info(f"Nexus file not found for run {_run_number}!")
            master_dict[_run_number][MasterDictKeys.monitor_counts] = None
            status_all_monitor_counts_found = False
            continue

        try:
            with h5py.File(_nexus_path, "r") as hdf5_data:
                monitor_counts = hdf5_data["entry"]["monitor1"]["total_counts"][0]
        except KeyError:
            monitor_counts = None
            status_all_monitor_counts_found = False
        master_dict[_run_number][MasterDictKeys.monitor_counts] = np.float32(monitor_counts)
    return status_all_monitor_counts_found


def update_dict_with_list_of_images(master_dict: dict) -> dict:
    """update the master dict with list of images"""
    for _run_number in master_dict.keys():
        list_tif = retrieve_list_of_tif(master_dict[_run_number][MasterDictKeys.data_path])
        logging.info(f"Retrieved {len(list_tif)} tif files for run {_run_number}!")
        master_dict[_run_number][MasterDictKeys.list_tif] = list_tif


def get_list_run_number(data_folder: str) -> list:
    """get list of run numbers from the data folder"""
    list_runs = glob.glob(os.path.join(data_folder, "Run_*"))
    list_run_number = [int(os.path.basename(run).split("_")[1]) for run in list_runs]
    return list_run_number


def update_dict_with_nexus_full_path(nexus_root_path: str, instrument: str, master_dict: dict) -> dict:
    """create dict of nexus path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.nexus_path] = os.path.join(
            nexus_root_path, f"{instrument}_{run_number}.nxs.h5"
        )


def update_with_nexus_metadata(master_dict: dict) -> dict:
    for run_number in master_dict.keys():
        nexus_path = master_dict[run_number][MasterDictKeys.nexus_path]
        if nexus_path is None or not os.path.exists(nexus_path):
            logging.info(f"Nexus file not found for run {run_number}!")
            continue
        detector_offset_us = get_detector_offset_from_nexus(nexus_path)
        master_dict[run_number][MasterDictKeys.detector_delay_us] = detector_offset_us

        _run_number = get_run_number_from_nexus(nexus_path)
        master_dict[run_number][MasterDictKeys.run_number] = _run_number


def update_dict_with_data_full_path(data_root_path: str, master_dict: dict) -> dict:
    """create dict of data path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.data_path] = os.path.join(data_root_path, f"Run_{run_number}")


def create_master_dict(
    data_dictionary: dict = None,
    data_type: DataType = DataType.sample,
    data_root_path: str = None,
    instrument: str = "VENUS",
    spectra_array: np.ndarray = None,
) -> tuple[dict, StatusMetadata]:
    logging.info(f"Create {data_type} master dict of : {data_dictionary.keys()}")

    if len(list(data_dictionary.keys())) == 0:
        logging.warning("No run numbers found in data dictionary!")
        return {}, StatusMetadata()

    status_metadata = StatusMetadata()

    # retrieve metadata for each run number
    master_dict = init_master_dict(data_dictionary)

    logging.info("updating with nexus metadata")
    update_with_nexus_metadata(master_dict)

    # logging.info("updating with shutter counts!")
    # master_dict, all_shutter_counts_found = update_dict_with_shutter_counts(master_dict)
    # if not all_shutter_counts_found:
    #     status_metadata.all_shutter_counts_found = False
    # logging.info(f"{master_dict = }")

    # if all_shutter_counts_found:
    logging.info("updating with spectra values!")
    master_dict, all_spectra_found = update_dict_with_spectra_files(master_dict, spectra_array=spectra_array)
    if not all_spectra_found:
        status_metadata.all_spectra_found = False
    logging.info(f"{master_dict = }")

    logging.info("updating with monitor counts!")
    all_monitor_counts_found = update_dict_with_monitor_counts(master_dict)
    if not all_monitor_counts_found:
        status_metadata.all_monitor_counts_found = False
    logging.info(f"{master_dict = }")

    logging.info("updating with proton charge!")
    all_proton_charge_found = update_dict_with_proton_charge(master_dict)
    if not all_proton_charge_found:
        status_metadata.all_proton_charge_found = False
    logging.info(f"{master_dict = }")

    logging.info("updating with list of images!")
    update_dict_with_list_of_images(master_dict)

    return master_dict, status_metadata


def produce_list_shutter_for_each_image(list_time_spectra: list = None, list_shutter_counts: list = None) -> list:
    """produce list of shutter counts for each image"""

    delat_time_spectra = list_time_spectra[1] - list_time_spectra[0]
    list_index_jump = np.where(np.diff(list_time_spectra) > delat_time_spectra)[0]
    list_index_jump = np.where(np.diff(list_time_spectra) > 0.0001)[0]

    logging.info(f"\t{list_index_jump = }")
    logging.info(f"\t{list_shutter_counts = }")

    list_shutter_values_for_each_image = np.zeros(len(list_time_spectra), dtype=np.float32)
    if len(list_shutter_counts) == 1:  # resonance mode
        list_shutter_values_for_each_image.fill(list_shutter_counts[0])
        return list_shutter_values_for_each_image

    list_shutter_values_for_each_image[0 : list_index_jump[0] + 1].fill(list_shutter_counts[0])
    for _index in range(1, len(list_index_jump)):
        _start = list_index_jump[_index - 1]
        _end = list_index_jump[_index]
        list_shutter_values_for_each_image[_start + 1 : _end + 1].fill(list_shutter_counts[_index])

    list_shutter_values_for_each_image[list_index_jump[-1] + 1 :] = list_shutter_counts[-1]

    return list_shutter_values_for_each_image


def replace_zero_with_local_median(data: np.ndarray, 
                                  kernel_size: Tuple[int, int, int] = (3, 3, 3),
                                  max_iterations: int = 10) -> np.ndarray:
    """
    Replace 0 values in a 3D array using local median filtering.

    This function ONLY processes small neighborhoods around 0 pixels,
    avoiding expensive computation on the entire dataset.
    
    Parameters:
    -----------
    data : np.ndarray
        3D input array that may contain 0 values
    kernel_size : Tuple[int, int, int]
        Size of the kernel for median filtering in (height, width, depth) format
        Default is (3, 3, 3)
    max_iterations : int
        Maximum number of iterations to replace 0 values
        Default is 10
    
    Returns:
    --------
    np.ndarray
        Array with 0 values replaced by local median values
    """
    # Work on a copy to avoid modifying the original data
    result = data.copy()

    # Track initial 0 count
    initial_zero_count = np.sum(result == 0)
    if initial_zero_count == 0:
        return result

    logging.info(f"Starting efficient 0 replacement with kernel size {kernel_size}")
    logging.info(f"Initial 0 count: {initial_zero_count}")

    # Calculate padding for kernel
    pad_h, pad_w, pad_d = [k // 2 for k in kernel_size]
    
    for iteration in range(max_iterations):
        # Find current 0 locations
        zero_coords = np.argwhere(result == 0)
        current_zero_count = len(zero_coords)

        if current_zero_count == 0:
            logging.info(f"All 0 values replaced after {iteration} iterations")
            break

        logging.info(f"Iteration {iteration + 1}: {current_zero_count} 0 values remaining")

        # Process each 0 pixel individually
        replaced_count = 0
        for coord in zero_coords:
            y, x, z = coord
            
            # Define the local neighborhood bounds
            y_min = max(0, y - pad_h)
            y_max = min(result.shape[0], y + pad_h + 1)
            x_min = max(0, x - pad_w)
            x_max = min(result.shape[1], x + pad_w + 1)
            z_min = max(0, z - pad_d)
            z_max = min(result.shape[2], z + pad_d + 1)
            
            # Extract the local neighborhood
            neighborhood = result[y_min:y_max, x_min:x_max, z_min:z_max]
            
            # Get non-NaN values in the neighborhood
            valid_values = neighborhood[~np.isnan(neighborhood)]
            
            # If we have valid values, compute median and replace
            if len(valid_values) > 0:
                median_value = np.median(valid_values)
                result[y, x, z] = median_value
                replaced_count += 1

        logging.info(f"  Replaced {replaced_count} zero values in this iteration")

        # If no progress was made, break
        if replaced_count == 0:
            remaining_zero_count = np.sum(result == 0)
            logging.info(f"No progress made. {remaining_zero_count} zero values could not be replaced")
            logging.info("(These may be in regions with no valid neighbors)")
            break

    final_zero_count = np.sum(result == 0)
    logging.info(f"Final zero count: {final_zero_count}")
    logging.info(f"Successfully replaced {initial_zero_count - final_zero_count} zero values")

    return result


def combine_dc_images(dc_master_dict: dict) -> np.ndarray:
    """combine all dc images
    
    Parameters:
    -----------
    dc_master_dict : dict
        master dict of dc run numbers
    
    Returns:
    --------
    np.ndarray
        combined dc data
    
    """
    logging.info("Combining all dark current images")
    full_dc_data = []
    logging.info(f"dc_master_dict = {dc_master_dict}")

    if not dc_master_dict:
        return None

    for _dc_run_number in dc_master_dict.keys():
        logging.info(f"Combining dc# {_dc_run_number} ...")
        dc_data = np.array(dc_master_dict[_dc_run_number][MasterDictKeys.data], dtype=np.float32)
        full_dc_data.append(dc_data)
        logging.info(f"{np.shape(full_dc_data) = }")

    logging.info("Combining all dc images is done!")
    logging.info(f"\tbefore: {len(full_dc_data) = }")
    dc_data_combined = np.array(full_dc_data).mean(axis=0)
    logging.info(f"\tafter: {dc_data_combined.shape = }")

    return dc_data_combined


def combine_ob_images(
    ob_master_dict: dict,
    use_proton_charge: bool = False,
    # use_monitor_counts: bool = False,
    use_shutter_counts: bool = False,
    replace_ob_zeros_by_nan: bool = False,
    replace_ob_zeros_by_local_median: bool = False,
    kernel_size_for_local_median: Tuple[int, int, int] = (3, 3, 3), 
    max_iterations: int = 10,
) -> Tuple[np.ndarray, float]:
    """combine all ob images and correct by proton charge and shutter counts
    
    Parameters:
    -----------
    ob_master_dict : dict
        master dict of ob run numbers
    use_proton_charge : bool
        whether to correct by proton charge
    use_monitor_counts : bool
        whether to correct by monitor counts
    use_shutter_counts : bool
        whether to correct by shutter counts
    replace_ob_zeros_by_nan : bool
        whether to replace ob zeros by nan
    replace_ob_zeros_by_local_median : bool
        whether to replace ob zeros by local median
    kernel_size : Tuple[int, int, int]
        kernel size for local median filtering
    max_iterations : int
        maximum number of iterations for local median filtering
    
    Returns:
    --------
    np.ndarray
        combined ob data
    float
        total proton charge used for correction
    
    """

    logging.info("Combining all open beam images")
    logging.info(f"\tcorrecting by proton charge: {use_proton_charge}")
    # logging.info(f"\tcorrecting by monitor counts: {use_monitor_counts}")
    logging.info(f"\tshutter counts: {use_shutter_counts}")
    logging.info(f"\treplace ob zeros by nan: {replace_ob_zeros_by_nan}")
    logging.info(f"\treplace ob zeros by local median: {replace_ob_zeros_by_local_median}")
    logging.info(f"\tkernel size for local median: y:{kernel_size_for_local_median[0]}, "
                 f"x:{kernel_size_for_local_median[1]}, "
                 f"tof:{kernel_size_for_local_median[2]}")
    full_ob_data_corrected = []

    if use_proton_charge:
        # used for the weighted sum of the ob data
        logging.info("Getting proton charge for each ob run number:")
        list_proton_charges = []
        for _ob_run_number in ob_master_dict.keys():
            proton_charge = ob_master_dict[_ob_run_number][MasterDictKeys.proton_charge]
            list_proton_charges.append(proton_charge)
            logging.info(f"\t ob# {_ob_run_number}: proton charge = {proton_charge} C")

        sum_proton_charge = np.sum(list_proton_charges)
        logging.info(f"\t Total proton charge of all ob runs: {sum_proton_charge} C")
    else:
        sum_proton_charge = 1.0  # dummy value to avoid division by zero

    for _ob_run_number in ob_master_dict.keys():
        logging.info(f"Combining ob# {_ob_run_number} ...")
        ob_data = np.array(ob_master_dict[_ob_run_number][MasterDictKeys.data], dtype=np.float32)

        # get statistics of ob data
        data_shape = ob_data.shape
        nbr_pixels = data_shape[1] * data_shape[2]
        logging.info(" **** Statistics of ob data *****")
        number_of_zeros = np.sum(ob_data == 0)
        logging.info(f"\t ob data shape: {data_shape}")
        logging.info(f"\t Number of zeros in ob data: {number_of_zeros}")
        logging.info(f"\t Percentage of zeros in ob data: {number_of_zeros / (data_shape[0] * nbr_pixels) * 100:.2f}%")
        logging.info(f"\t Mean of ob data: {np.mean(ob_data)}")
        logging.info(f"\t maximum of ob data: {np.max(ob_data)}")
        logging.info(f"\t minimum of ob data: {np.min(ob_data)}")
        logging.info("**********************************")

        if use_proton_charge:
            logging.info("\t -> Normalized by proton charge")
            proton_charge = ob_master_dict[_ob_run_number][MasterDictKeys.proton_charge]
            logging.info(f"\t\t proton charge: {proton_charge} C")
            logging.info(f"\t\t{type(proton_charge) = }")
            logging.info(f"\t\tbefore division: {proton_charge.dtype = }")
            ob_data *= (proton_charge / sum_proton_charge) # weighted sum
            logging.info(f"\t\tafter division: {ob_data.dtype = }")
            logging.info(f"{ob_data.shape = }")

        # if use_monitor_counts:
        #     logging.info("\t -> Normalized by monitor counts")
        #     monitor_counts = ob_master_dict[_ob_run_number][MasterDictKeys.monitor_counts]
        #     logging.info(f"\t\t monitor counts: {monitor_counts}")
        #     logging.info(f"\t\t{type(monitor_counts) = }")
        #     ob_data = ob_data / monitor_counts
        #     logging.info(f"{ob_data.shape = }")

        if use_shutter_counts:
            logging.info("\t -> Normalized by shutter counts")

            list_shutter_values_for_each_image = produce_list_shutter_for_each_image(
                list_time_spectra=ob_master_dict[_ob_run_number][MasterDictKeys.list_spectra],
                list_shutter_counts=ob_master_dict[_ob_run_number][MasterDictKeys.shutter_counts],
            )

            logging.info(f"{list_shutter_values_for_each_image.shape = }")
            temp_ob_data = np.empty_like(ob_data, dtype=np.float32)
            for _index in range(len(list_shutter_values_for_each_image)):
                temp_ob_data[_index] = ob_data[_index] / list_shutter_values_for_each_image[_index]
            logging.info(f"{temp_ob_data.shape = }")
            ob_data = temp_ob_data.copy()

        # ob_data_combined = np.array(ob_data).mean(axis=0)
        # logging.info(f"{ob_data_combined.shape = }")

        if replace_ob_zeros_by_local_median:
            ob_data = replace_zero_with_local_median(ob_data, 
                                                     kernel_size=kernel_size_for_local_median, 
                                                     max_iterations=max_iterations)

        full_ob_data_corrected.append(ob_data)
        logging.info(f"{np.shape(full_ob_data_corrected) = }")

    logging.info("Combining all ob images is done!")
    logging.info(f"\tbefore: {len(full_ob_data_corrected) = }")
    if use_proton_charge:
        ob_data_combined = np.array(full_ob_data_corrected).sum(axis=0)
    else:
        ob_data_combined = np.array(full_ob_data_corrected).mean(axis=0)
        
    logging.info(f"\tafter: {ob_data_combined.shape = }")

    # remove zeros
    if replace_ob_zeros_by_nan:
        ob_data_combined[ob_data_combined == 0] = np.nan

    return ob_data_combined, sum_proton_charge


def combine_images(
    data_type: DataType.sample,
    master_dict: dict,
    use_proton_charge: bool = False,
    # use_monitor_counts: bool = False,
    # use_shutter_counts: bool = False,
    replace_zeros_by_nan: bool = False,
    replace_zeros_by_local_median: bool = False,
    kernel_size_for_local_median: Tuple[int, int, int] = (3, 3, 3), 
    max_iterations: int = 10,
) -> Tuple[np.ndarray, float]:
    """combine all images and correct by proton charge and shutter counts
    
    Parameters:
    -----------
    master_dict : dict
        master dict of run numbers
    use_proton_charge : bool
        whether to correct by proton charge
    use_monitor_counts : bool
        whether to correct by monitor counts
    use_shutter_counts : bool
        whether to correct by shutter counts
    replace_zeros_by_nan : bool
        whether to replace zeros by nan
    replace_zeros_by_local_median : bool
        whether to replace zeros by local median
    kernel_size : Tuple[int, int, int]
        kernel size for local median filtering
    max_iterations : int
        maximum number of iterations for local median filtering
    
    Returns:
    --------
    np.ndarray
        combined data
    float
        total proton charge used for correction
    
    """

    logging.info(f"Combining all {data_type} images")
    logging.info(f"\tcorrecting by proton charge: {use_proton_charge}")
    # logging.info(f"\tcorrecting by monitor counts: {use_monitor_counts}")
    # logging.info(f"\tshutter counts: {use_shutter_counts}")
    logging.info(f"\treplace zeros by nan: {replace_zeros_by_nan}")
    logging.info(f"\treplace zeros by local median: {replace_zeros_by_local_median}")
    logging.info(f"\tkernel size for local median: y:{kernel_size_for_local_median[0]}, "
                 f"x:{kernel_size_for_local_median[1]}, "
                 f"tof:{kernel_size_for_local_median[2]}")
    full_data_corrected = []

    if use_proton_charge:
        # used for the weighted sum of the ob data
        logging.info(f"Getting proton charge for each {data_type} run number:")
        list_proton_charges = []
        for _run_number in master_dict.keys():
            proton_charge = master_dict[_run_number][MasterDictKeys.proton_charge]
            list_proton_charges.append(proton_charge)
            logging.info(f"\t {data_type}# {_run_number}: proton charge = {proton_charge} C")

        sum_proton_charge = np.sum(list_proton_charges)
        logging.info(f"\t Total proton charge of all {data_type} runs: {sum_proton_charge} C")
    else:
        sum_proton_charge = 1.0  # dummy value to avoid division by zero

    for _run_number in master_dict.keys():
        logging.info(f"Combining {data_type}# {_run_number} ...")
        data = np.array(master_dict[_run_number][MasterDictKeys.data], dtype=np.float32)

        # get statistics of data
        data_shape = data.shape
        nbr_pixels = data_shape[1] * data_shape[2]
        logging.info(f" **** Statistics of {data_type} data *****")
        number_of_zeros = np.sum(data == 0)
        logging.info(f"\t {data_type} data shape: {data_shape}")
        logging.info(f"\t Number of zeros in {data_type} data: {number_of_zeros}")
        logging.info(f"\t Percentage of zeros in {data_type} data: {number_of_zeros / (data_shape[0] * nbr_pixels) * 100:.2f}%")
        logging.info(f"\t Mean of {data_type} data: {np.mean(data)}")
        logging.info(f"\t maximum of {data_type} data: {np.max(data)}")
        logging.info(f"\t minimum of {data_type} data: {np.min(data)}")
        logging.info("**********************************")

        if use_proton_charge:
            logging.info("\t -> Normalized by proton charge")
            proton_charge = master_dict[_run_number][MasterDictKeys.proton_charge]
            logging.info(f"\t\t proton charge: {proton_charge} C")
            logging.info(f"\t\t{type(proton_charge) = }")
            logging.info(f"\t\tbefore division: {proton_charge.dtype = }")
            data *= (proton_charge / sum_proton_charge) # weighted sum
            logging.info(f"\t\tafter division: {data.dtype = }")
            logging.info(f"{data.shape = }")

        if replace_zeros_by_local_median:
            data = replace_zero_with_local_median(data, 
                                                kernel_size=kernel_size_for_local_median, 
                                                max_iterations=max_iterations)

        full_data_corrected.append(data)
        logging.info(f"{np.shape(full_data_corrected) = }")

    logging.info("Combining all ob images is done!")
    logging.info(f"\tbefore: {len(full_data_corrected) = }")
    if use_proton_charge:
        data_combined = np.array(full_data_corrected).sum(axis=0)
    else:
        data_combined = np.array(full_data_corrected).mean(axis=0)
        
    logging.info(f"\tafter: {data_combined.shape = }")

    # remove zeros
    if replace_zeros_by_nan:
        data_combined[data_combined == 0] = np.nan

    return data_combined, sum_proton_charge


# def normalization_by_shutter_counts(sample_master_dict=None,
#                 _sample_run_number=None,
#                 _sample_data=None,
#                 ob_master_dict=None,
#                 first_ob_run_number=None,
#             ):
#     """
#     Normalize sample data by shutter counts for each image.
    
#     This function normalizes sample data by dividing each image by its corresponding
#     shutter count value. The shutter count values are determined by mapping the time
#     spectra from the open beam data to the shutter counts recorded for the sample.
#     Images with zero shutter counts are replaced with NaN values to avoid division
#     by zero errors.
    
#     Parameters
#     ----------
#     sample_master_dict : dict, optional
#         Master dictionary containing sample run data and metadata including shutter counts.
#         Expected to have structure: {run_number: {MasterDictKeys.shutter_counts: list, ...}}
#     _sample_run_number : str or int, optional
#         The run number key to access the specific sample data in sample_master_dict
#     _sample_data : numpy.ndarray, optional
#         3D array of sample image data with shape (n_images, height, width)
#     ob_master_dict : dict, optional
#         Master dictionary containing open beam run data and metadata including time spectra.
#         Expected to have structure: {run_number: {MasterDictKeys.list_spectra: list, ...}}
#     first_ob_run_number : str or int, optional
#         The run number key to access the time spectra from the first open beam run
        
#     Returns
#     -------
#     numpy.ndarray
#         Normalized sample data array with same shape as input _sample_data.
#         Images corresponding to zero shutter counts are set to NaN.
        
#     Notes
#     -----
#     The normalization process involves:
#     1. Extracting time spectra from the open beam data
#     2. Extracting shutter counts from the sample data
#     3. Mapping shutter count values to each image based on time spectra
#     4. Dividing each sample image by its corresponding shutter count
#     5. Setting images with zero shutter counts to NaN
    
#     This function is typically used in neutron imaging data processing where
#     shutter counts represent the exposure time or beam intensity for each image.
    
#     Examples
#     --------
#     >>> normalized_data = normalization_by_shutter_counts(
#     ...     sample_master_dict=sample_dict,
#     ...     _sample_run_number="Run_12345",
#     ...     _sample_data=sample_images,
#     ...     ob_master_dict=ob_dict,
#     ...     first_ob_run_number="Run_12340"
#     ... )
#     """
        
#     list_shutter_values_for_each_image = produce_list_shutter_for_each_image(
#         list_time_spectra=ob_master_dict[first_ob_run_number][MasterDictKeys.list_spectra],
#         list_shutter_counts=sample_master_dict[_sample_run_number][MasterDictKeys.shutter_counts],
#     )

#     sample_data = []
#     for _sample, _shutter_value in zip(_sample_data, list_shutter_values_for_each_image, strict=False):
#         if _shutter_value != 0:
#             sample_data.append(_sample / _shutter_value)
#         else:
#             sample_data.append(np.nan)
#     _sample_data = np.array(sample_data)

#     return _sample_data


def perform_normalization(_sample_data=None, ob_data_combined=None, dc_data_combined=None):
    
    # working on each image (TOF) independently
    if dc_data_combined is not None:
        logging.info(f"normalization with DC subtraction")
        _normalized_data = np.divide(np.subtract(_sample_data, dc_data_combined), np.subtract(ob_data_combined, dc_data_combined), 
                                        out=np.zeros_like(_sample_data), 
                                        where=(ob_data_combined - dc_data_combined)!=0)
    else:
        logging.info(f"normalization without DC subtraction")
        _normalized_data = np.divide(_sample_data, ob_data_combined, 
                                        out=np.zeros_like(_sample_data), 
                                         where=ob_data_combined!=0)

    _normalized_data[ob_data_combined == 0] = 0
    
    # Integration of sample, dc and ob and then division
    if dc_data_combined is not None:
        logging.info(f"normalization with DC subtraction - integrated")
        _integrated_normalized_data = np.divide(np.subtract(np.sum(_sample_data, axis=0), np.sum(dc_data_combined, axis=0)),    
                                                np.subtract(np.sum(ob_data_combined, axis=0), np.sum(dc_data_combined, axis=0)), 
                                        out=np.zeros_like(np.sum(_sample_data, axis=0)), 
                                        where=(np.sum(ob_data_combined, axis=0) - np.sum(dc_data_combined, axis=0))!=0)
    else:
        logging.info(f"normalization without DC subtraction - integrated")
        _integrated_normalized_data = np.divide(np.sum(_sample_data, axis=0), np.sum(ob_data_combined, axis=0), 
                                        out=np.zeros_like(np.sum(_sample_data, axis=0)), 
                                         where=np.sum(ob_data_combined, axis=0)!=0)

    return {'normalized_data': _normalized_data,
            'integrated_normalized_data': _integrated_normalized_data}


def perform_spectrum_normalization(roi=None, sample_data=None, ob_data_combined_for_spectrum=None, dc_data_combined=None, dc_data_combined_for_spectrum=None):
    _spectrum_normalized_data = None
    if roi is not None:
        x0 = roi.left
        y0 = roi.top
        width = roi.width
        height = roi.height

        _sample_data_combined_for_spectrum = [np.sum(np.sum(_data[y0: y0+height, x0: x0+width], axis=0), axis=0) for _data in sample_data]

        if dc_data_combined is not None:
            _spectrum_normalized_data = np.divide(np.subtract(_sample_data_combined_for_spectrum, dc_data_combined_for_spectrum), 
                                                    np.subtract(ob_data_combined_for_spectrum, dc_data_combined_for_spectrum), 
                                                    out=np.zeros_like(_sample_data_combined_for_spectrum), 
                                                    where=(ob_data_combined_for_spectrum - dc_data_combined_for_spectrum)!=0)
        else:
            _spectrum_normalized_data = np.divide(_sample_data_combined_for_spectrum, ob_data_combined_for_spectrum, 
                                                    out=np.zeros_like(_sample_data_combined_for_spectrum), 
                                                    where=ob_data_combined_for_spectrum!=0)
        logging.info(f"{np.shape(_spectrum_normalized_data) = }")
    return _spectrum_normalized_data


def export_normalized_data(ob_master_dict=None, 
                sample_master_dict=None, 
                _sample_run_number=None,
                normalized_data=None, 
                integrated_normalized_data=None,
                _spectrum_normalized_data=None,
                lambda_array=None, 
                energy_array=None, 
                output_folder="./", 
                export_corrected_stack_of_normalized_data=False,
                export_corrected_integrated_normalized_data=False,
                roi=None,
                spectra_array=None,
                spectra_file=None,):

    logging.info("Exporting normalized data ...")

    list_ob_runs = list(ob_master_dict.keys())
    str_ob_runs = "_".join([str(_ob_run_number) for _ob_run_number in list_ob_runs])
    full_output_folder = os.path.join(
        output_folder, f"normalized_sample_{_sample_run_number}_obs_{str_ob_runs}"
    )  # issue for WEI here !
    full_output_folder = os.path.abspath(full_output_folder)
    os.makedirs(full_output_folder, exist_ok=True)

    if roi is not None:
        logging.info(f"\t -> exporting the spectrum normalization")
        logging.info(f"{roi =}")
        x0 = roi.left
        y0 = roi.top
        width = roi.width
        height = roi.height
        full_file_name = os.path.join(full_output_folder, "spectrum_normalization_profile.txt")
        pd_dataframe = pd.DataFrame({
            "file_index": np.arange(len(lambda_array)),
            "lambda (Angstroms)": lambda_array,
            "energy (eV)": energy_array,
            "spectrum normalization": _spectrum_normalized_data
        })
        pd_dataframe.attrs['roi [left, top, width, height]'] = f"{x0}, {y0}, {width}, {height}"
                        
        with open(full_file_name, 'w') as f:
            # Write metadata as comments
            for key, value in pd_dataframe.attrs.items():
                f.write(f"# {key}: {value}\n")
            
            # Write the DataFrame
            pd_dataframe.to_csv(f, index=False)              
        
        pd_dataframe.to_csv(full_file_name, index=False, sep=",")
        logging.info(f"\t -> Exporting the spectrum normalization profile to {full_file_name}")

    if export_corrected_integrated_normalized_data:
        # making up the integrated sample data
        full_file_name = os.path.join(full_output_folder, "normalized_integrated.tif")
        logging.info(f"\t -> Exporting integrated normalized data to {full_file_name} ...")
        make_tiff(data=integrated_normalized_data[_sample_run_number], filename=full_file_name)
        logging.info(f"\t -> Exporting integrated normalized data to {full_file_name} is done!")

    if export_corrected_stack_of_normalized_data:
        output_stack_folder = os.path.join(full_output_folder, "stack")
        logging.info(f"\tmaking folder {output_stack_folder}")
        os.makedirs(output_stack_folder, exist_ok=True)

        for _index, _data in enumerate(normalized_data[_sample_run_number]):
            _output_file = os.path.join(output_stack_folder, f"image{_index:04d}.tif")
            make_tiff(data=_data, filename=_output_file)
        logging.info(f"\t -> Exporting normalized data to {output_stack_folder} is done!")
        print(f"Exported normalized tif images are in: {output_stack_folder}!")
        
        # spectra_file = sample_master_dict[_sample_run_number][MasterDictKeys.spectra_file_name]
        export_spectra_file(spectra_array=spectra_array,
                            spectra_file=spectra_file,
                            output_stack_folder=output_stack_folder,
                            normalized_data=normalized_data[_sample_run_number])


        # create x-axis file
        create_x_axis_file(
            lambda_array=lambda_array,
            energy_array=energy_array,
            output_folder=output_stack_folder,
        )


def manually_create_and_export_spectra_file(spectra_array=None, output_folder=None, normalized_data=None):
     # manually create the file for spectra
        spectra_file_name = os.path.join(output_folder, f"manually_created_{SPECTRA_FILE_PREFIX}")
        _full_counts_array = np.empty_like(spectra_array)
        for _index, _data in enumerate(normalized_data):
            _full_counts_array[_index] = np.nansum(_data)
        pd_spectra = pd.DataFrame({
            "shutter_time": spectra_array,
            "counts": _full_counts_array
        })
        pd_spectra.to_csv(spectra_file_name, index=False, sep=",")
        logging.info(f"\t -> Exporting manually created spectra file to {spectra_file_name} is done!")


def export_spectra_file(spectra_array=None,
                            spectra_file=None,
                            output_stack_folder=None,
                            normalized_data=None):

    if spectra_array is not None:
        manually_create_and_export_spectra_file(spectra_array=spectra_array,
                                                output_folder=output_stack_folder,
                                                normalized_data=normalized_data)

    else:

        if spectra_file and Path(spectra_file).exists():
            logging.info(f"Exported time spectra file  {spectra_file} to {output_stack_folder}!")
            shutil.copy(spectra_file, output_stack_folder)


def  export_corrected_normalized_data(sample_master_dict=None,
                                      ob_master_dict=None,
                                       combined_normalized_data=None,
                                       integrated_normalized_data=None,
                                       export_corrected_integrated_combined_normalized_data=False,
                                       export_corrected_stack_of_combined_normalized_data=False,
                                       lambda_array=None,
                                       energy_array=None,
                                       output_folder="./",
                                       spectra_array=None
):

    list_sample_runs = list(sample_master_dict.keys())
    _sample_str = ""
    for _run in list_sample_runs:
        _sample_str += f"{sample_master_dict[_run]['run_number']}_"

    _ob_str = ""
    list_ob_runs = list(ob_master_dict.keys())
    for _run in list_ob_runs:
        _ob_str += f"{ob_master_dict[_run]['run_number']}_"

    full_output_folder = os.path.join(
        output_folder, f"combined_normalized_samples_{_sample_str}_obs_{_ob_str}"
    )  # issue for WEI here !
    full_output_folder = os.path.abspath(full_output_folder)
    os.makedirs(full_output_folder, exist_ok=True)

    if export_corrected_integrated_combined_normalized_data:
        # making up the integrated sample data
        data_integrated = np.nanmean(combined_normalized_data, axis=0)
        full_file_name = os.path.join(full_output_folder, "integrated.tif")
        logging.info(f"\t -> Exporting integrated combined normalized data to {full_file_name} ...")
        make_tiff(data=data_integrated, filename=full_file_name)
        logging.info(f"\t -> Exporting integrated combined normalized data to {full_file_name} is done!")

    if export_corrected_stack_of_combined_normalized_data:
        output_stack_folder = os.path.join(full_output_folder, "stack")
        logging.info(f"\tmaking folder {output_stack_folder}")
        os.makedirs(output_stack_folder, exist_ok=True)

        for _index, _data in enumerate(combined_normalized_data):
            _output_file = os.path.join(output_stack_folder, f"image{_index:04d}.tif")
            make_tiff(data=_data, filename=_output_file)
        logging.info(f"\t -> Exporting combined normalized data to {output_stack_folder} is done!")
        print(f"Exported combined normalized tif images are in: {output_stack_folder}!")
        
        export_spectra_file(spectra_array=spectra_array,
                            spectra_file=spectra_file,
                            output_stack_folder=output_stack_folder,
                            normalized_data=combined_normalized_data)


        # copy one of the spectra file to the output folder, or the manually defined one
        spectra_file = sample_master_dict[list_sample_runs[0]][MasterDictKeys.spectra_file_name]
        export_spectra_file(spectra_array=spectra_array,
                            spectra_file=spectra_file,
                            output_stack_folder=output_stack_folder,
                            normalized_data=combined_normalized_data)

        # create x-axis file
        create_x_axis_file(
            lambda_array=lambda_array,
            energy_array=energy_array,
            output_folder=output_stack_folder,
        )


def read_container_roi_file(container_roi_file=None) -> tuple[int, int, int, int]:
        master_dict = load_json(container_roi_file)
        list_container_values = master_dict['list_container_values']
        return list_container_values
        
        
def save_container_roi_file(output_folder:str,
                            sample_run_number: str, 
                            container_roi: Roi, 
                            list_container_values: list, 
                            integrated_image: np.ndarray):
    # container_roi_file = os.path.join(output_folder, f"container_roi_of_run_{sample_run_number}.tiff")
    container_roi_file = os.path.join(output_folder, f"container_roi_of_run_{sample_run_number}.json")
    
    logging.info(f"Saving container roi file to {container_roi_file}")
    # scitiff_dict = {'container_roi': container_roi,
    #                 'list_container_values': list_container_values,
    #                 }
    
    integrated_image = integrated_image.astype(float)
    list_container_values = [float(_value) for _value in list_container_values]
    master_dict = {'integrated_image': integrated_image.tolist(),
                   'container_roi': {'left': float(container_roi.left),
                                     'top': float(container_roi.top),
                                     'width': float(container_roi.width),
                                     'height': float(container_roi.height)},
                   'list_container_values': list_container_values}
    
    save_json(container_roi_file, master_dict)
    return container_roi_file
    
    
def normalize_by_container_roi(sample_data: np.ndarray, 
                               container_roi: Roi,
                               container_roi_file: str,
                               output_folder: str,
                               sample_run_number: str) -> np.ndarray:
    """normalize sample data subtracting by container roi"""

    logging.info(f"in normalize_by_container_roi:")
    if container_roi_file is not None:
        logging.info(f"\t {container_roi_file = }")
        _container_value_array: float = read_container_roi_file(container_roi_file=container_roi_file)
        logging.info(f"\t{_container_value_array =}")
        
        _normalized_sample = np.empty_like(sample_data)
        for i, _sample in enumerate(sample_data):
            _container_value = _container_value_array[i]
            _log_sample = -np.log(_sample)
            _log_container_value = -np.log(_container_value)
            _log_normalized_sample = _log_sample - _log_container_value
            _normalized_sample[i] = np.exp(- _log_normalized_sample)

    else:
        logging.info(f"\t {container_roi = }")
        x0: int = container_roi.left
        y0: int = container_roi.top
        width: int = container_roi.width
        height: int = container_roi.height
        
        _normalized_sample = np.empty_like(sample_data)
        list_container_values = []
        for i, _sample in enumerate(sample_data):
            _container_value = np.mean(np.mean(_sample[y0:y0 + height, x0:x0 + width], axis=0), axis=0)            
            list_container_values.append(_container_value)
            _log_sample = -np.log(_sample)
            _log_container_value = -np.log(_container_value)
            _log_normalized_sample = _log_sample - _log_container_value
            _normalized_sample[i] = np.exp(- _log_normalized_sample)
        
        # save the container roi file
        container_roi_file = save_container_roi_file(output_folder=output_folder, 
                                                    sample_run_number=sample_run_number, 
                                                    container_roi=container_roi,
                                                    list_container_values=list_container_values,
                                                    integrated_image=np.sum(sample_data, axis=0))    
        
    return _normalized_sample, container_roi_file


def logging_statistics_of_data(data=None, data_type=DataType.sample):
        data_shape = data.shape
        nbr_pixels = data_shape[1] * data_shape[2]
        logging.info(f" **** Statistics of {data_type} data *****")
        number_of_zeros = np.sum(data == 0)
        logging.info(f"\t {data_type} data shape: {data_shape}")
        logging.info(f"\t data type of _sample_data: {data.dtype}")
        logging.info(f"\t Number of zeros in {data_type} data: {number_of_zeros}")
        logging.info(f"\t Number of nan in {data_type} data: {np.sum(np.isnan(data))}")
        logging.info(f"\t Percentage of zeros in {data_type} data: {number_of_zeros / (data_shape[0] * nbr_pixels) * 100:.2f}%")
        logging.info(f"\t Mean of {data_type} data: {np.mean(data)}")
        logging.info(f"\t maximum of {data_type} data: {np.max(data)}")
        logging.info(f"\t minimum of {data_type} data: {np.min(data)}")
        logging.info("**********************************")