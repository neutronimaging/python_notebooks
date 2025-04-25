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
from IPython.display import display
from IPython.core.display import HTML
import pandas as pd

LOG_PATH = "/SNS/VENUS/shared/log/"
LOAD_DTYPE = np.uint16

PROTON_CHARGE_TOLERANCE = 0.1

file_name, ext = os.path.splitext(os.path.basename(__file__))
log_file_name = os.path.join(LOG_PATH, f"{file_name}.log")
logging.basicConfig(filename=log_file_name,
                    filemode='w',
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    level=logging.INFO)
logging.info(f"*** Starting a new script {file_name} ***")


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
                                    output_tif: bool = True) -> None | np.ndarray:
    """normalize the sample data with ob data using proton charge and shutter counts"""
    # list sample and ob run numbers
    logging.info(f"{sample_run_numbers = }")
    if verbose:
        display(HTML(f"Sample run numbers: {sample_run_numbers}"))

    logging.info(f"{ob_run_numbers = }")
    if verbose:
        display(HTML(f"List of ob run numbers: {ob_run_numbers}"))

    logging.info(f"{output_folder = }")
    logging.info(f"{nexus_path = }")

    sample_master_dict, sample_status_metadata = create_master_dict(list_run_numbers=sample_run_numbers, 
                                                             data_type=DataType.sample,   
                                                             nexus_root_path=nexus_path)
    ob_master_dict, ob_status_metadata = create_master_dict(list_run_numbers=ob_run_numbers, 
                                                         data_type=DataType.ob, 
                                                         nexus_root_path=nexus_path)                                                         
    
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

    normalized_by_proton_charge = (sample_status_metadata.all_proton_charge_found and ob_status_metadata.all_proton_charge_found)
    normalized_by_shutter_counts = (sample_status_metadata.all_shutter_counts_found and ob_status_metadata.all_shutter_counts_found)

    # combine all ob images
    ob_data_combined = combine_ob_images(ob_master_dict, 
                                         use_proton_charge=normalized_by_proton_charge, 
                                         use_shutter_counts=normalized_by_shutter_counts)
    logging.info(f"{ob_data_combined.shape = }")
    if verbose:
        display(HTML(f"{ob_data_combined.shape = }"))

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
        logging.info(f"{ob_data_combined.shape = }")

        _sample_data /= ob_data_combined

        normalized_data[_sample_run_number] = _sample_data

    logging.info(f"Normalization is done!")
    if verbose:
        display(HTML(f"Normalization is done!"))

    if output_tif:
        logging.info(f"Exporting normalized data to {output_folder} ...")
        if verbose:
            display(HTML(f"Exporting normalized data to {output_folder} ..."))

        # make up new output folder name
        sample_folder = os.path.dirname(sample_run_numbers[0])
        logging.info(f"{sample_folder = }")
        logging.info(f"{sample_run_numbers[0] =}")
        full_output_folder = os.path.join(output_folder, os.path.basename(sample_folder) + "_normalized")

        for _run_number in normalized_data.keys():
            logging.info(f"\t -> Exporting run {_run_number} ...")
            if verbose:
                display(HTML(f"\t -> Exporting run {_run_number} ..."))
            run_number_output_folder = os.path.join(full_output_folder, f"Run_{_run_number}_normalized")
            os.makedirs(run_number_output_folder, exist_ok=True)
            
            _list_data = normalized_data[_run_number]
            for _index, _data in enumerate(_list_data):
                _output_file = os.path.join(run_number_output_folder, f"image{_index:04d}.tif")
                make_tiff(data=_data, filename=_output_file)
            logging.info(f"\t -> Exporting run {_run_number} is done!")
            if verbose:
                display(HTML(f"\t -> Exporting run {_run_number} is done!"))

            print(f"Exported tif images are in: {run_number_output_folder}!")

        logging.info(f"export folder: {run_number_output_folder}")
        logging.info(f"Exporting normalized data is done!")
        if verbose:
            display(HTML(f"Exporting normalized data is done!"))

    else:
        return normalized_data


def normalization(sample_folder=None, ob_folder=None, output_folder="./", verbose=False):
    pass

    # list sample and ob run numbers
#     list_sample_run_numbers = get_list_run_number(sample_folder)
#     logging.info(f"{list_sample_run_numbers = }")
#     if verbose:
#         display(HTML(f"List of sample run numbers: {list_sample_run_numbers}"))

#     list_ob_run_numbers = get_list_run_number(ob_folder)
#     logging.info(f"{list_ob_run_numbers = }")
#     if verbose:
#         display(HTML(f"List of ob run numbers: {list_ob_run_numbers}"))

#     sample_master_dict, sample_status_metadata = create_master_dict(list_run_numbers=list_sample_run_numbers, 
#                                                              data_type='sample', 
#                                                              data_root_path=sample_folder)
#     ob_master_dict, ob_status_metadata = create_master_dict(list_run_numbers=list_ob_run_numbers, 
#                                                          data_type='ob', 
#                                                          data_root_path=ob_folder)
                                                             
#     # load ob images
#     for _ob_run_number in ob_master_dict.keys():
#         logging.info(f"loading ob# {_ob_run_number} ... ")
#         if verbose:
#             display(HTML(f"Loading ob# {_ob_run_number} ..."))
#         ob_master_dict[_ob_run_number][MasterDictKeys.data] = load_data_using_multithreading(ob_master_dict[_ob_run_number][MasterDictKeys.list_tif], combine_tof=False)
#         logging.info(f"ob# {_ob_run_number} loaded!")
#         logging.info(f"{ob_master_dict[_ob_run_number][MasterDictKeys.data].shape = }")
#         if verbose:
#             display(HTML(f"ob# {_ob_run_number} loaded!"))
#             display(HTML(f"{ob_master_dict[_ob_run_number][MasterDictKeys.data].shape = }"))

#     normalized_by_proton_charge = (sample_status_metadata.all_proton_charge_found and ob_status_metadata.all_proton_charge_found)
#     normalized_by_shutter_counts = (sample_status_metadata.all_shutter_counts_found and ob_status_metadata.all_shutter_counts_found)

#     # combine all ob images
#     ob_data_combined = combine_ob_images(ob_master_dict, 
#                                          use_proton_charge=normalized_by_proton_charge, 
#                                          use_shutter_counts=normalized_by_shutter_counts)
#     logging.info(f"{ob_data_combined.shape = }")
#     if verbose:
#         display(HTML(f"{ob_data_combined.shape = }"))

#     # load sample images
#     for _sample_run_number in sample_master_dict.keys():
#         logging.info(f"loading sample# {_sample_run_number} ... ")
#         if verbose:
#             display(HTML(f"Loading sample# {_sample_run_number} ..."))
#         sample_master_dict[_sample_run_number][MasterDictKeys.data] = load_data_using_multithreading(sample_master_dict[_sample_run_number][MasterDictKeys.list_tif], combine_tof=False)
#         logging.info(f"sample# {_sample_run_number} loaded!")
#         logging.info(f"{sample_master_dict[_sample_run_number][MasterDictKeys.data].shape = }")
#         if verbose:
#             display(HTML(f"sample# {_sample_run_number} loaded!"))
#             display(HTML(f"{sample_master_dict[_sample_run_number][MasterDictKeys.data].shape = }"))

#     normalized_data = {}

#     # normalize the sample data
#     for _sample_run_number in list_sample_run_numbers:
#         logging.info(f"normalization of run {_sample_run_number}")
#         if verbose:
#             display(HTML(f"Normalization of run {_sample_run_number}"))

#         _sample_data = np.array(sample_master_dict[_sample_run_number][MasterDictKeys.data], dtype=np.float32)

#         if normalized_by_proton_charge:
#             proton_charge = sample_master_dict[_sample_run_number][MasterDictKeys.proton_charge]
#             _sample_data = _sample_data / proton_charge

#         if normalized_by_shutter_counts:
#             shutter_counts = sample_master_dict[_sample_run_number][MasterDictKeys.shutter_counts]
            
#             delta_shutter_counts = shutter_counts[1] - shutter_counts[0]
#             list_index_jump = np.where(np.diff(shutter_counts) > delta_shutter_counts)[0]

#             list_shutter_counts = sample_master_dict[_sample_run_number][MasterDictKeys.shutter_counts]

#             list_shutter_values_for_each_image = np.zeros_like(sample_master_dict[_sample_run_number][MasterDictKeys.list_tif], dtype=np.float32)
#             list_shutter_values_for_each_image[0: list_index_jump[0]].fill(list_shutter_counts[0])
#             for _index in range(1, len(list_index_jump)):
#                 _start = list_index_jump[_index - 1]
#                 _end = list_index_jump[_index]
#                 list_shutter_values_for_each_image[_start: _end].fill(list_shutter_counts[_index])

#             list_shutter_values_for_each_image[list_index_jump[-1]:] = list_shutter_counts[-1]

#             logging.info(f"{list_shutter_values_for_each_image.shape = }")
#             logging.info(f"{_sample_data.shape = }")
#             logging.info(f"{set(list_shutter_values_for_each_image) = }")
#             _sample_data = _sample_data / list_shutter_values_for_each_image

#         _sample_data /= ob_data_combined

#         normalized_data[_sample_run_number] = _sample_data

#     logging.info(f"Normalization is done!")
#     if verbose:
#         display(HTML(f"Normalization is done!"))

#     logging.info(f"Exporting normalized data to {output_folder} ...")
#     if verbose:
#         display(HTML(f"Exporting normalized data to {output_folder} ..."))

#     # make up new output folder name
#     full_output_folder = os.path.join(output_folder, os.path.basename(sample_folder) + "_normalized")

#     for _run_number in normalized_data.keys():
#         logging.info(f"\t -> Exporting run {_run_number} ...")
#         if verbose:
#             display(HTML(f"\t -> Exporting run {_run_number} ..."))
#         run_number_output_folder = os.path.join(full_output_folder, f"Run_{_run_number}_normalized")
#         os.makedirs(run_number_output_folder, exist_ok=True)
        
#         _list_data = normalized_data[_run_number]
#         for _index, _data in enumerate(_list_data):
#             _output_file = os.path.join(run_number_output_folder, f"image{_index:04d}.tif")
#             make_tiff(data=_data, filename=_output_file)
#         logging.info(f"\t -> Exporting run {_run_number} is done!")
#         if verbose:
#             display(HTML(f"\t -> Exporting run {_run_number} is done!"))

#     logging.info(f"Exporting normalized data is done!")
#     if verbose:
#         display(HTML(f"Exporting normalized data is done!"))


def make_tiff(data: list, filename: str = "", metadata: dict = None) -> None:
    new_image = Image.fromarray(np.array(data))
    if metadata:
        new_image.save(filename, tiffinfo=metadata)
    else:
        new_image.save(filename)


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
    return master_dict, status_all_proton_charge_found
   

def update_dict_with_list_of_images(master_dict: dict) -> dict:
    """update the master dict with list of images"""
    for _run_number in master_dict.keys():
        list_tif = retrieve_list_of_tif(master_dict[_run_number][MasterDictKeys.data_path])
        master_dict[_run_number][MasterDictKeys.list_tif] = list_tif
    return master_dict


def get_list_run_number(data_folder: str) -> list:
    """get list of run numbers from the data folder"""
    list_runs = glob.glob(os.path.join(data_folder, "Run_*"))
    list_run_number = [int(os.path.basename(run).split("_")[1]) for run in list_runs]
    return list_run_number


def update_dict_with_nexus_full_path(nexus_root_path: str, master_dict: dict) -> dict:
    """create dict of nexus path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.nexus_path] = os.path.join(nexus_root_path, f"VENUS_{run_number}.nxs.h5")
    return master_dict


def update_dict_with_data_full_path(data_root_path: str, master_dict: dict) -> dict:
    """create dict of data path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.data_path] = os.path.join(data_root_path, f"Run_{run_number}")
    return master_dict


def create_master_dict(list_run_numbers: list = None, 
                       data_type: DataType = DataType.sample, 
                       data_root_path: str = None, 
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
    master_dict = update_dict_with_data_full_path(data_root_path, master_dict)

    logging.info(f"updating with nexus full path!")
    master_dict = update_dict_with_nexus_full_path(nexus_root_path, master_dict)

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
    master_dict, all_proton_charge_found = update_dict_with_proton_charge(master_dict)
    if not all_proton_charge_found:
        status_metadata.all_proton_charge_found = False
    logging.info(f"{master_dict = }")

    logging.info(f"updating with list of images!")
    master_dict = update_dict_with_list_of_images(master_dict)

    return master_dict, status_metadata


def produce_list_shutter_for_each_image(list_time_spectra:list = None, list_shutter_counts:list = None) -> list:
    """produce list of shutter counts for each image"""

    delat_time_spectra = list_time_spectra[1] - list_time_spectra[0]
    list_index_jump = np.where(np.diff(list_time_spectra) > delat_time_spectra)[0]
    list_index_jump = np.where(np.diff(list_time_spectra) > 0.0001)[0]

    logging.info(f"\t{list_index_jump = }")

    # delta_shutter_counts = shutter_counts[1] - shutter_counts[0]
    # list_index_jump = np.where(np.diff(shutter_counts) > delta_shutter_counts)[0]

    list_shutter_values_for_each_image = np.zeros(len(list_time_spectra), dtype=np.float32)
    list_shutter_values_for_each_image[0: list_index_jump[0]].fill(list_shutter_counts[0])
    for _index in range(1, len(list_index_jump)):
        _start = list_index_jump[_index - 1]
        _end = list_index_jump[_index]
        list_shutter_values_for_each_image[_start: _end].fill(list_shutter_counts[_index])

    list_shutter_values_for_each_image[list_index_jump[-1]:] = list_shutter_counts[-1]

    return list_shutter_values_for_each_image


def combine_ob_images(ob_master_dict: dict,  use_proton_charge: bool = False, use_shutter_counts: bool = False) -> np.ndarray:
    """combine all ob images and correct by proton charge and shutter counts"""

    logging.info(f"Combining all open beam images and correcting by proton charge and shutter counts ...")
    full_ob_data_corrected = []

    for _ob_run_number in ob_master_dict.keys():
        logging.info(f"Combining ob# {_ob_run_number} ...")
        ob_data = np.array(ob_master_dict[_ob_run_number][MasterDictKeys.data], dtype=np.float32)
        logging.info(f"{ob_data.shape = }")

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

        full_ob_data_corrected.append(ob_data)
        logging.info(f"{np.shape(full_ob_data_corrected) = }")

    ob_data_combined = np.array(full_ob_data_corrected).mean(axis=0)
    logging.info(f"{ob_data_combined.shape = }")

    # remove zeros
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