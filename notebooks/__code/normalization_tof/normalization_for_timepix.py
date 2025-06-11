import argparse
import logging
import os
import h5py
import glob
import numpy as np
from skimage.io import imread
import numpy as np
import multiprocessing as mp 
from PIL import Image
import shutil
from IPython.display import display
from IPython.core.display import HTML
import pandas as pd
import matplotlib.pyplot as plt
# from enum import Enum
# from scipy.constants import h, c, electron_volt, m_n

from __code.normalization_tof.units import convert_array_from_time_to_lambda, convert_array_from_time_to_energy
from __code.normalization_tof.units import TimeUnitOptions, DistanceUnitOptions, EnergyUnitOptions

LOG_PATH = "/SNS/VENUS/shared/log/"
LOAD_DTYPE = np.uint16

PROTON_CHARGE_TOLERANCE = 0.1

file_name, ext = os.path.splitext(os.path.basename(__file__))
user_name = os.getlogin() # add user name to the log file name
log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
logging.basicConfig(filename=log_file_name,
                    filemode='w',
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    level=logging.INFO)
logging.info(f"*** Starting a new script {file_name} ***")


class PLOT_SIZE:
    width =  8
    height = 5


class DataType:
    sample = "sample"
    ob = "ob"
    unknown = "unknown"


class MasterDictKeys:
    frame_number = "frame_number"
    proton_charge = "proton_charge"
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
    all_spectra_found = True
    all_proton_charge_found = True


def _worker(fl):
    return (imread(fl).astype(LOAD_DTYPE)).swapaxes(0,1)


def load_data_using_multithreading(list_tif: list = None, combine_tof: bool = False) -> np.ndarray:
    """load data using multithreading"""
    with mp.Pool(processes=40) as pool:
        data = pool.map(_worker, list_tif)

    if combine_tof:
        return np.array(data).sum(axis=0)
    else:
        return np.array(data)


def retrieve_list_of_tif(folder: str) -> list:
    """retrieve list of tif files in the folder"""
    list_tif = glob.glob(os.path.join(folder, "*.tif*"))
    list_tif.sort()
    return list_tif


def normalization_with_list_of_runs(sample_run_numbers: list = None, 
                                    ob_run_numbers: list = None, 
                                    output_folder: str ="./", 
                                    nexus_path: str = None,
                                    verbose: bool = False,
                                    proton_charge_flag=True,
                                    shutter_counts_flag=True,
                                    replace_ob_zeros_by_nan_flag=False, 
                                    output_tif: bool = True,
                                    instrument: str = "VENUS",
                                    detector_delay_us: float = None,
                                    preview: bool = False,
                                    distance_source_detector_m: float = 25,
                                    export_mode: dict = None) -> None | np.ndarray:
    """normalize the sample data with ob data using proton charge and shutter counts
    
    parameters:
    sample_run_numbers: list of full path of sample run numbers (ex: ['/SNS/VENUS/IPTS-36035/shared/autoreduce/mcp/images/Run_8747'])
    ob_run_numbers: list of full path of ob run numbers (ex: ['/SNS/VENUS/IPTS-36035/shared/autoreduce/mcp/images/Run_8748'])
    output_folder: path to the output folder
    nexus_path: path to the nexus folder
    verbose: whether to display verbose output
    proton_charge_flag: whether to use proton charge for normalization
    shutter_counts_flag: whether to use shutter counts for normalization
    replace_ob_zeros_by_nan_flag: whether to replace ob zeros by NaN
    output_tif: whether to output TIF files
    preview: whether to preview the results
    distance_source_detector_m: distance from source to detector in meters
    export_mode: dictionary specifying export options

    """

    # list sample and ob run numbers
    logging.info(f"{sample_run_numbers = }")
    if verbose:
        display(HTML(f"Sample run numbers: {sample_run_numbers}"))

    logging.info(f"{ob_run_numbers = }")
    if verbose:
        display(HTML(f"List of ob run numbers: {ob_run_numbers}"))

    logging.info(f"{output_folder = }")
    logging.info(f"{nexus_path = }")

    export_corrected_stack_of_sample_data = export_mode.get("sample_stack", False)
    export_corrected_stack_of_ob_data = export_mode.get("ob_stack", False)
    export_corrected_stack_of_normalized_data = export_mode.get("normalized_stack", False)
    export_corrected_integrated_sample_data = export_mode.get("sample_integrated", False)
    export_corrected_integrated_ob_data = export_mode.get("ob_integrated", False)
    export_corrected_integrated_normalized_data = export_mode.get("normalized_integrated", False)

    logging.info(f"{export_corrected_stack_of_sample_data = }")
    logging.info(f"{export_corrected_stack_of_ob_data = }")
    logging.info(f"{export_corrected_stack_of_normalized_data = }")
    logging.info(f"{export_corrected_integrated_sample_data = }")
    logging.info(f"{export_corrected_integrated_ob_data = }")
    logging.info(f"{export_corrected_integrated_normalized_data = }")

    sample_master_dict, sample_status_metadata = create_master_dict(list_run_numbers=sample_run_numbers, 
                                                             data_type=DataType.sample,
                                                             instrument=instrument,   
                                                             nexus_root_path=nexus_path)
    ob_master_dict, ob_status_metadata = create_master_dict(list_run_numbers=ob_run_numbers, 
                                                         data_type=DataType.ob, 
                                                         instrument=instrument,
                                                         nexus_root_path=nexus_path)                                                         
    
    # only for SNAP
    if instrument == "SNAP":
        for _run in sample_master_dict.keys():
            sample_master_dict[_run][MasterDictKeys.detector_delay_us] = detector_delay_us  

        for _run in ob_master_dict.keys():
            ob_master_dict[_run][MasterDictKeys.detector_delay_us] = detector_delay_us

    # load ob images
    for _ob_run_number in ob_master_dict.keys():
        logging.info(f"loading ob# {_ob_run_number} ... ")
        if verbose:
            display(HTML(f"Loading ob# {_ob_run_number} ..."))
        ob_master_dict[_ob_run_number][MasterDictKeys.data] = load_data_using_multithreading(ob_master_dict[_ob_run_number][MasterDictKeys.list_tif], combine_tof=False)
        logging.info(f"ob# {_ob_run_number} loaded!")
        logging.info(f"{ob_master_dict[_ob_run_number][MasterDictKeys.data].shape = }")
        if verbose:
            display(HTML(f"ob# {_ob_run_number} loaded!"))
            display(HTML(f"{ob_master_dict[_ob_run_number][MasterDictKeys.data].shape = }"))

    if proton_charge_flag:
        normalized_by_proton_charge = (sample_status_metadata.all_proton_charge_found and ob_status_metadata.all_proton_charge_found)
    else:
        normalized_by_proton_charge = False
    
    if shutter_counts_flag:
        normalized_by_shutter_counts = (sample_status_metadata.all_shutter_counts_found and ob_status_metadata.all_shutter_counts_found)
    else:
        normalized_by_shutter_counts = False

    # combine all ob images
    ob_data_combined = combine_ob_images(ob_master_dict, 
                                         use_proton_charge=normalized_by_proton_charge, 
                                         use_shutter_counts=normalized_by_shutter_counts,
                                         replace_ob_zeros_by_nan=replace_ob_zeros_by_nan_flag,
                                             )
    logging.info(f"{ob_data_combined.shape = }")
    if verbose:
        display(HTML(f"{ob_data_combined.shape = }"))

    # export ob data if requested
    if export_corrected_stack_of_ob_data or export_corrected_integrated_ob_data:       
        export_ob_images(ob_run_numbers, 
                         output_folder, 
                         export_corrected_stack_of_ob_data, 
                         export_corrected_integrated_ob_data, 
                         ob_data_combined,
                         spectra_file_name=ob_master_dict[_ob_run_number][MasterDictKeys.spectra_file_name])

      # load sample images
    for _sample_run_number in sample_master_dict.keys():
        logging.info(f"loading sample# {_sample_run_number} ... ")
        if verbose:
            display(HTML(f"Loading sample# {_sample_run_number} ..."))
        sample_master_dict[_sample_run_number][MasterDictKeys.data] = load_data_using_multithreading(sample_master_dict[_sample_run_number][MasterDictKeys.list_tif], combine_tof=False)
        logging.info(f"sample# {_sample_run_number} loaded!")
        logging.info(f"{sample_master_dict[_sample_run_number][MasterDictKeys.data].shape = }")
        if verbose:
            display(HTML(f"sample# {_sample_run_number} loaded!"))
            display(HTML(f"{sample_master_dict[_sample_run_number][MasterDictKeys.data].shape = }"))

    normalized_data = {}

    # normalize the sample data
    for _sample_run_number in sample_master_dict.keys():
        logging.info(f"normalization of run {_sample_run_number}")
        if verbose:
            display(HTML(f"Normalization of run {_sample_run_number}"))

        _sample_data = np.array(sample_master_dict[_sample_run_number][MasterDictKeys.data], dtype=np.float32)

        # get statistics of sample data
        data_shape = _sample_data.shape
        nbr_pixels = data_shape[1] * data_shape[2]
        logging.info(f" **** Statistics of sample data *****")
        number_of_zeros = np.sum(_sample_data == 0)
        logging.info(f"\t ob data shape: {data_shape}")
        logging.info(f"\t Number of zeros in ob data: {number_of_zeros}")
        logging.info(f"\t Percentage of zeros in ob data: {number_of_zeros / (data_shape[0] * nbr_pixels) * 100:.2f}%")
        logging.info(f"\t Mean of ob data: {np.mean(_sample_data)}")
        logging.info(f"\t maximum of ob data: {np.max(_sample_data)}")
        logging.info(f"\t minimum of ob data: {np.min(_sample_data)}")
        logging.info(f"**********************************")        

        if normalized_by_proton_charge:
            proton_charge = sample_master_dict[_sample_run_number][MasterDictKeys.proton_charge]
            _sample_data = _sample_data / proton_charge

        if normalized_by_shutter_counts:
            list_shutter_values_for_each_image = produce_list_shutter_for_each_image(list_time_spectra=ob_master_dict[_ob_run_number][MasterDictKeys.list_spectra],
                                                                                      list_shutter_counts=sample_master_dict[_sample_run_number][MasterDictKeys.shutter_counts],
                                                                                      )
            
            sample_data = []
            for _sample, _shutter_value in zip(_sample_data, list_shutter_values_for_each_image):
                sample_data.append(_sample / _shutter_value)
            _sample_data = np.array(sample_data)

        logging.info(f"{_sample_data.shape = }")
        logging.info(f"{_sample_data.dtype = }")
        logging.info(f"{ob_data_combined.shape = }")
        logging.info(f"{ob_data_combined.dtype = }")

        # export sample data after correction if requested
        if export_corrected_stack_of_sample_data or export_corrected_integrated_sample_data:
            export_sample_images(output_folder, 
                                 export_corrected_stack_of_sample_data, 
                                 export_corrected_integrated_sample_data, 
                                 _sample_run_number, 
                                 _sample_data,
                                 spectra_file_name=sample_master_dict[_sample_run_number][MasterDictKeys.spectra_file_name])

        # _sample_data = np.divide(_sample_data, ob_data_combined, out=np.zeros_like(_sample_data), where=ob_data_combined!=0)
        # _sample_data = np.divide(_sample_data, ob_data_combined, out=np.zeros_like(_sample_data))
        # _sample_data = np.divide(_sample_data, ob_data_combined, out=np.zeros_like(_sample_data), where=ob_data_combined!=0)
        _normalized_data = np.zeros_like(_sample_data, dtype=np.float32)
        index = 0
        for _sample, _ob in zip(_sample_data, ob_data_combined):
            _normalized_data[index] = np.divide(_sample, _ob)
            index += 1

        normalized_data[_sample_run_number] = _normalized_data

        # normalized_data[_sample_run_number] = np.array(np.divide(_sample_data, ob_data_combined))
        logging.info(f"{normalized_data[_sample_run_number].shape = }")
        logging.info(f"{normalized_data[_sample_run_number].dtype = }")    

        detector_delay_us = sample_master_dict[_sample_run_number][MasterDictKeys.detector_delay_us]
        time_spectra = sample_master_dict[_sample_run_number][MasterDictKeys.list_spectra]

        lambda_array = convert_array_from_time_to_lambda(time_array=time_spectra,
                                                          time_unit=TimeUnitOptions.s,
                                                          distance_source_detector=distance_source_detector_m,
                                                          distance_source_detector_unit=DistanceUnitOptions.m,
                                                          detector_offset=detector_delay_us,
                                                          detector_offset_unit=TimeUnitOptions.us,
                                                          lambda_unit=DistanceUnitOptions.angstrom)
        energy_array = convert_array_from_time_to_energy(time_array=time_spectra,
                                                         time_unit=TimeUnitOptions.s,
                                                         distance_source_detector=distance_source_detector_m,
                                                         distance_source_detector_unit=DistanceUnitOptions.m,
                                                         detector_offset=detector_delay_us,
                                                         detector_offset_unit=TimeUnitOptions.us,
                                                         energy_unit=EnergyUnitOptions.eV)

        if preview:

            # display preview of normalized data
            fig, axs1 = plt.subplots(1, 2, figsize=(2*PLOT_SIZE.width, PLOT_SIZE.height))
            sample_data_integrated = np.nanmean(_sample_data, axis=0)
            im0 = axs1[0].imshow(sample_data_integrated, cmap='gray')
            plt.colorbar(im0, ax=axs1[0])
            axs1[0].set_title(f"Sample data: {_sample_run_number} | detector delay: {detector_delay_us:.2f} us")
    
            sample_integrated1 = np.nansum(_sample_data, axis=1)
            sample_integrated = np.nansum(sample_integrated1, axis=1)
            axs1[1].plot(sample_integrated)
            axs1[1].set_xlabel("File image index")
            axs1[1].set_ylabel("mean of full image")
            plt.tight_layout

            fig, axs2 = plt.subplots(1, 2, figsize=(2*PLOT_SIZE.width, PLOT_SIZE.height))
            ob_data_integrated = np.nanmean(ob_data_combined, axis=0)
            im1 = axs2[0].imshow(ob_data_integrated, cmap='gray')
            plt.colorbar(im1, ax=axs2[0])
            axs2[0].set_title(f"OB combinded data ")

            ob_integrated1 = np.nansum(ob_data_combined, axis=1)
            ob_integrated = np.nansum(ob_integrated1, axis=1)
            axs2[1].plot(ob_integrated)
            axs2[1].set_xlabel("File image index")
            axs2[1].set_ylabel("mean of full image")
            plt.tight_layout()

            fig, axs3 = plt.subplots(1, 2, figsize=(2*PLOT_SIZE.width, PLOT_SIZE.height))
            normalized_data_integrated = np.nanmean(normalized_data[_sample_run_number], axis=0)
            im2 = axs3[0].imshow(normalized_data_integrated, cmap='gray')
            plt.colorbar(im2, ax=axs3[0])
            axs3[0].set_title(f"Normalized data {_sample_run_number}")

            profile_step1 = np.nanmean(normalized_data[_sample_run_number], axis=1)
            profile = np.nanmean(profile_step1, axis=1)
            axs3[1].plot(profile)
            axs3[1].set_xlabel("File image index")
            axs3[1].set_ylabel("mean of full image")          
            plt.tight_layout()

            fig, axs4 = plt.subplots(1, 2, figsize=(2*PLOT_SIZE.width, PLOT_SIZE.height))
            axs4[0].plot(lambda_array, profile, '*')
            axs4[0].set_xlabel("Lambda (A)")
            axs4[0].set_ylabel("mean of full image")

            axs4[1].plot(energy_array, profile, '*')
            axs4[1].set_xlabel("Energy (eV)")
            axs4[1].set_ylabel("mean of full image")
            axs4[1].set_xscale('log')
            plt.tight_layout()

            plt.show()

        if export_corrected_integrated_normalized_data or export_corrected_stack_of_normalized_data:
            # make up new output folder name

            list_ob_runs = list(ob_master_dict.keys())
            str_ob_runs = "_".join([str(_ob_run_number) for _ob_run_number in list_ob_runs])
            full_output_folder = os.path.join(output_folder, f"normalized_sample_{_sample_run_number}_obs_{str_ob_runs}")                 # issue for WEI here !
            os.makedirs(full_output_folder, exist_ok=True)

            if export_corrected_integrated_normalized_data:
                # making up the integrated sample data
                sample_data_integrated = np.nanmean(normalized_data[_sample_run_number], axis=0)
                full_file_name = os.path.join(full_output_folder, "integrated.tif")
                logging.info(f"\t -> Exporting integrated normalized data to {full_file_name} ...")
                make_tiff(data=sample_data_integrated, filename=full_file_name)
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
                logging.info(f"Exported time spectra file  to {full_output_folder}!")
                spectra_file = sample_master_dict[_sample_run_number][MasterDictKeys.spectra_file_name]
                shutil.copy(spectra_file, full_output_folder)

    logging.info(f"Normalization and export is done!")
    if verbose:
        display(HTML(f"Normalization and export is done!"))


def get_detector_offset_from_nexus(nexus_path: str) -> float:
    """get the detector offset from the nexus file"""
    with h5py.File(nexus_path, 'r') as hdf5_data:
        try:
            detector_offset_micros = hdf5_data['entry']['DASlogs']['BL10:Det:TH:DSPT1:TIDelay']['value'][0]
        except KeyError:
            detector_offset_micros = None
    return detector_offset_micros


def export_sample_images(output_folder, 
                         export_corrected_stack_of_sample_data, 
                         export_corrected_integrated_sample_data, 
                         _sample_run_number, 
                         _sample_data,
                         spectra_file_name=None):
    logging.info(f"> Exporting sample corrected images to {output_folder} ...")

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
        shutil.copy(spectra_file_name, os.path.join(output_stack_folder))
        logging.info(f"\t -> Exporting spectra file {spectra_file_name} to {output_stack_folder} is done!")

    if export_corrected_integrated_sample_data:
                # making up the integrated sample data
        sample_data_integrated = np.nanmean(_sample_data, axis=0)
        full_file_name = os.path.join(sample_output_folder, "integrated.tif")
        logging.info(f"\t -> Exporting integrated sample data to {full_file_name} ...")
        make_tiff(data=sample_data_integrated, filename=full_file_name)
        logging.info(f"\t -> Exporting integrated sample data to {full_file_name} is done!")


def export_ob_images(ob_run_numbers, 
                     output_folder, 
                     export_corrected_stack_of_ob_data, 
                     export_corrected_integrated_ob_data, 
                     ob_data_combined,
                     spectra_file_name):
    """export ob images to the output folder"""
    logging.info(f"> Exporting combined ob images to {output_folder} ...")
    logging.info(f"\t{ob_run_numbers = }")
    list_ob_runs_number_only = [str(isolate_run_number_from_full_path(_ob_run_number)) for _ob_run_number in ob_run_numbers]
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
        # copy spectra file to the output folder
        shutil.copy(spectra_file_name, os.path.join(output_stack_folder))
        logging.info(f"\t -> Exported spectra file {spectra_file_name} to {output_stack_folder}!")


def normalization(sample_folder=None, ob_folder=None, output_folder="./", verbose=False):
    pass


def make_tiff(data: list, filename: str = "", metadata: dict = None) -> None:
    new_image = Image.fromarray(np.array(data))
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
    run_number = run_number.split("_")[1]
    return int(run_number)


def init_master_dict(list_run_numbers: list[str]) -> dict:
    master_dict = {}

    for run_number_full_path in list_run_numbers:
        run_number = isolate_run_number(run_number_full_path)
        master_dict[run_number] = {MasterDictKeys.nexus_path: None, 
                                   MasterDictKeys.frame_number: None, 
                                   MasterDictKeys.data_path: None, 
                                   MasterDictKeys.proton_charge: None,
                                   MasterDictKeys.matching_ob: [] ,
                                   MasterDictKeys.list_tif: [], 
                                   MasterDictKeys.list_spectra: None,
                                   MasterDictKeys.spectra_file_name: None,
                                   MasterDictKeys.detector_delay_us: None,
                                   MasterDictKeys.data: None}

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
            with open(shutter_count_file, 'r') as f:
                lines = f.readlines()
                list_shutter_counts = []
                for _line in lines:
                    _, _value = _line.strip().split("\t")
                    if _value == "0":
                        break
                    list_shutter_counts.append(float(_value))
                master_dict[run_number][MasterDictKeys.shutter_counts] = list_shutter_counts        
    return master_dict, status_all_shutter_counts_found


def update_dict_with_spectra_files(master_dict: dict) -> tuple[dict, bool]:
    """update the master dict with spectra values from spectra file"""
    status_all_spectra_found = True
    for _run_number in master_dict.keys():
        data_path = master_dict[_run_number][MasterDictKeys.data_path]
        _list_files = glob.glob(os.path.join(data_path, "*_Spectra.txt"))
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
        try:
            with h5py.File(_nexus_path, 'r') as hdf5_data:
                proton_charge = hdf5_data['entry'][MasterDictKeys.proton_charge][0] / 1e12
        except KeyError:
            proton_charge = None
            status_all_proton_charge_found = False
        master_dict[_run_number][MasterDictKeys.proton_charge] = proton_charge        
    return status_all_proton_charge_found
   

def update_dict_with_list_of_images(master_dict: dict) -> dict:
    """update the master dict with list of images"""
    for _run_number in master_dict.keys():
        list_tif = retrieve_list_of_tif(master_dict[_run_number][MasterDictKeys.data_path])
        master_dict[_run_number][MasterDictKeys.list_tif] = list_tif


def get_list_run_number(data_folder: str) -> list:
    """get list of run numbers from the data folder"""
    list_runs = glob.glob(os.path.join(data_folder, "Run_*"))
    list_run_number = [int(os.path.basename(run).split("_")[1]) for run in list_runs]
    return list_run_number


def update_dict_with_nexus_full_path(nexus_root_path: str, instrument: str, master_dict: dict) -> dict:
    """create dict of nexus path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.nexus_path] = os.path.join(nexus_root_path, f"{instrument}_{run_number}.nxs.h5")


def update_with_nexus_metadata(master_dict: dict) -> dict:
    for run_number in master_dict.keys():
        nexus_path = master_dict[run_number][MasterDictKeys.nexus_path]
        detector_offset_us = get_detector_offset_from_nexus(nexus_path)
        master_dict[run_number][MasterDictKeys.detector_delay_us] = detector_offset_us


def update_dict_with_data_full_path(data_root_path: str, master_dict: dict) -> dict:
    """create dict of data path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.data_path] = os.path.join(data_root_path, f"Run_{run_number}")


def create_master_dict(list_run_numbers: list = None, 
                       data_type: DataType = DataType.sample, 
                       data_root_path: str = None, 
                       instrument: str = "VENUS",
                       nexus_root_path: str = None) -> tuple[dict, StatusMetadata]:
    logging.info(f"Create {data_type} master dict of runs: {list_run_numbers = }")

    status_metadata = StatusMetadata()

    if data_root_path is None:
        data_root_path = os.path.dirname(list_run_numbers[0])

    if nexus_root_path is None:
        nexus_root_path = retrieve_root_nexus_full_path(data_root_path)
    logging.info(f"{nexus_root_path =}")

    # retrieve metadata for each run number
    master_dict = init_master_dict(list_run_numbers)

    logging.info(f"updating with data full path!")
    update_dict_with_data_full_path(data_root_path, master_dict)

    logging.info(f"updating with nexus full path!")
    update_dict_with_nexus_full_path(nexus_root_path, instrument, master_dict)

    logging.info(f"updating with nexus metadata")
    update_with_nexus_metadata(master_dict)

    logging.info(f"updating with shutter counts!")
    master_dict, all_shutter_counts_found = update_dict_with_shutter_counts(master_dict)
    if not all_shutter_counts_found:
        status_metadata.all_shutter_counts_found = False
    logging.info(f"{master_dict = }")

    if all_shutter_counts_found:
        logging.info(f"updating with spectra values!")
        master_dict, all_spectra_found = update_dict_with_spectra_files(master_dict)
        if not all_spectra_found:
            status_metadata.all_spectra_found = False
        logging.info(f"{master_dict = }")

    logging.info(f"updating with proton charge!")
    all_proton_charge_found = update_dict_with_proton_charge(master_dict)
    if not all_proton_charge_found:
        status_metadata.all_proton_charge_found = False
    logging.info(f"{master_dict = }")

    logging.info(f"updating with list of images!")
    update_dict_with_list_of_images(master_dict)

    return master_dict, status_metadata


def produce_list_shutter_for_each_image(list_time_spectra:list = None, list_shutter_counts:list = None) -> list:
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

    list_shutter_values_for_each_image[0: list_index_jump[0]+1].fill(list_shutter_counts[0])
    for _index in range(1, len(list_index_jump)):
        _start = list_index_jump[_index - 1]
        _end = list_index_jump[_index]
        list_shutter_values_for_each_image[_start+1: _end+1].fill(list_shutter_counts[_index])

    list_shutter_values_for_each_image[list_index_jump[-1]+1:] = list_shutter_counts[-1]

    return list_shutter_values_for_each_image


def combine_ob_images(ob_master_dict: dict,  
                      use_proton_charge: bool = False, 
                      use_shutter_counts: bool = False,
                      replace_ob_zeros_by_nan: bool = False,
                      ) -> np.ndarray:

    """combine all ob images and correct by proton charge and shutter counts"""

    logging.info(f"Combining all open beam images")
    logging.info(f"\tcorrecting by proton charge: {use_proton_charge}")
    logging.info(f"\tshutter counts: {use_shutter_counts}")
    logging.info(f"\treplace ob zeros by nan: {replace_ob_zeros_by_nan}")
    full_ob_data_corrected = []

    for _ob_run_number in ob_master_dict.keys():
        logging.info(f"Combining ob# {_ob_run_number} ...")
        ob_data = np.array(ob_master_dict[_ob_run_number][MasterDictKeys.data], dtype=np.float32)

        # get statistics of ob data
        data_shape = ob_data.shape
        nbr_pixels = data_shape[1] * data_shape[2]
        logging.info(f" **** Statistics of ob data *****")
        number_of_zeros = np.sum(ob_data == 0)
        logging.info(f"\t ob data shape: {data_shape}")
        logging.info(f"\t Number of zeros in ob data: {number_of_zeros}")
        logging.info(f"\t Percentage of zeros in ob data: {number_of_zeros / (data_shape[0] * nbr_pixels) * 100:.2f}%")
        logging.info(f"\t Mean of ob data: {np.mean(ob_data)}")
        logging.info(f"\t maximum of ob data: {np.max(ob_data)}")
        logging.info(f"\t minimum of ob data: {np.min(ob_data)}")
        logging.info(f"**********************************")

        if use_proton_charge:
            logging.info(f"\t -> Normalized by proton charge")
            proton_charge = ob_master_dict[_ob_run_number][MasterDictKeys.proton_charge]
            ob_data = ob_data / proton_charge
            logging.info(f"{ob_data.shape = }")

        if use_shutter_counts:
            logging.info(f"\t -> Normalized by shutter counts")

            list_shutter_values_for_each_image = produce_list_shutter_for_each_image(list_time_spectra=ob_master_dict[_ob_run_number][MasterDictKeys.list_spectra],
                                                                                      list_shutter_counts=ob_master_dict[_ob_run_number][MasterDictKeys.shutter_counts],
                                                                                      )
           
            logging.info(f"{list_shutter_values_for_each_image.shape = }")
            temp_ob_data = np.empty_like(ob_data, dtype=np.float32)
            for _index in range(len(list_shutter_values_for_each_image)):
                temp_ob_data[_index] = ob_data[_index] / list_shutter_values_for_each_image[_index]
            logging.info(f"{temp_ob_data.shape = }")
            ob_data = temp_ob_data.copy()

        ob_data_combined = np.array(ob_data).mean(axis=0)
        logging.info(f"{ob_data_combined.shape = }")

        # remove zeros
        if replace_ob_zeros_by_nan:
            ob_data[ob_data == 0] = np.NaN

        # if True:
        #     # replace zeros in OB by median of surrounding pixels
        #     where_ob_zeros = np.where(ob_data == 0)
        #     logging.info(f"{len(where_ob_zeros) = }")
        #     if len(where_ob_zeros[0]) > 0:
        #         logging.info(f"Replacing zeros in OB data by median of surrounding pixels ...")
        #         # if verbose:
        #         #     display(HTML(f"Replacing zeros in OB data by median of surrounding pixels ..."))
        #         for _index in range(len(where_ob_zeros[0])):
        #             _t = where_ob_zeros[0][_index]
        #             _y = where_ob_zeros[1][_index]
        #             _x = where_ob_zeros[2][_index]
        #             ob_data[_t, _y, _x] = np.nanmedian(ob_data[_t, _y-1:_y+2, _x-1:_x+2]) 

        full_ob_data_corrected.append(ob_data)
        logging.info(f"{np.shape(full_ob_data_corrected) = }")

    ob_data_combined = np.array(full_ob_data_corrected).mean(axis=0)
    logging.info(f"{ob_data_combined.shape = }")

    # remove zeros
    if replace_ob_zeros_by_nan:
        ob_data_combined[ob_data_combined == 0] = np.NaN

    return ob_data_combined


if __name__ == '__main__':

    # sample_master_dict = {'run_number': {'nexus_path': 'path', 'frame_number': 'value', 'proton_charge': 'value', 'matching_ob': []}}

    parser = argparse.ArgumentParser(description="Normalized Timepix data with shutter counts and proton charge",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument("--sample", type=str, nargs=1, help="Full path to sample run number")
    parser.add_argument("--ob", type=str, nargs=1, help="Full path to the ob run number")
    parser.add_argument("--output", type=str, nargs=1, help="Path to the output folder", default="./")
    
    args = parser.parse_args()
    logging.info(f"{args = }")

    try:
        sample_run_number = args.sample[0]
        if not os.path.exists(sample_run_number):
            logging.info(f"sample run number {sample_run_number} does not exist!")
            raise FileNotFoundError(f"Folder {sample_run_number} does not exist!")
        else:
            logging.info(f"sample run number {sample_run_number} located!")

    except (TypeError, FileNotFoundError):
        print("\n *** INPUT ERROR of sample run number! ***\n")
        print(parser.print_help())
        exit()
    
    try:
        ob_run_number = args.ob[0]
        if not os.path.exists(ob_run_number):
            logging.info(f"open beam run number {ob_run_number} does not exist!")
            raise FileNotFoundError(f"Folder {ob_run_number} does not exist!")
        else:
            logging.info(f"open beam run number {ob_run_number} located!")

    except (TypeError, FileNotFoundError):
        print("\n *** INPUT ERROR of ob folder! ***\n")
        print(parser.print_help())
        exit()

    try:
        output_folder = args.output[0]
    
    except TypeError:
        print("\n *** INPUT ERROR of output folder! ***\n")
        print(parser.print_help())
        exit()

    normalization_with_list_of_runs(sample_run_numbers=[sample_run_number],
                                    ob_run_numbers=[ob_run_number], 
                                    output_folder=output_folder, 
                                    nexus_path=retrieve_root_nexus_full_path(sample_run_number),
                                    verbose=False)

    # normalization(sample_folder=sample_folder, ob_folder=ob_folder, output_folder=output_folder)

    print(f"Normalization is done! Check the log file {log_file_name} for more details!")
    print(f"Exported data to {output_folder}")

    # sample = /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_Sample6_UA_H_Batteries_1_5_Angs_min_30Hz_5C
    # ob = /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_OB_for_UA_H_Batteries_1_5_Angs_min_30Hz_5C

    # full command to use to test code
    
    # source /opt/anaconda/etc/profile.d/conda.sh
    # conda activate ImagingReduction
    # > python normalization_for_timepix.py --sample /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_Sample6_UA_H_Batteries_1_5_Angs_min_30Hz_5C --ob /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_OB_for_UA_H_Batteries_1_5_Angs_min_30Hz_5C --output /SNS/VENUS/IPTS-34808/shared/processed_data/jean_test