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


class MasterDictKeys:
    frame_number = "frame_number"
    proton_charge = "proton_charge"
    matching_ob = "matching_ob"
    list_tif = "list_tif"
    data = "data"
    nexus_path = "nexus_path"
    data_path = "data_path"
    

class StatusMetadata:
    all_frame_number_found = True
    all_proton_charge_found = True


def _worker(fl):
    return (imread(fl).astype(LOAD_DTYPE)).swapaxes(0,1)


def load_data_using_multithreading(list_tif, combine_tof=False):
    with mp.Pool(processes=40) as pool:
        data = pool.map(_worker, list_tif)

    if combine_tof:
        return np.array(data).sum(axis=0)
    else:
        return np.array(data)


def retrieve_list_of_tif(folder):
    list_tif = glob.glob(os.path.join(folder, "*.tif*"))
    list_tif.sort()
    return list_tif


def normalization(sample_folder=None, ob_folder=None, output_folder="./", verbose=False):

    # list sample and ob run numbers
    list_sample_run_numbers = get_list_run_number(sample_folder)
    logging.info(f"{list_sample_run_numbers = }")
    if verbose:
        display(HTML(f"List of sample run numbers: {list_sample_run_numbers}"))

    list_ob_run_numbers = get_list_run_number(ob_folder)
    logging.info(f"{list_ob_run_numbers = }")
    if verbose:
        display(HTML(f"List of ob run numbers: {list_ob_run_numbers}"))

    sample_master_dict, sample_status_metadata = create_master_dict(list_run_numbers=list_sample_run_numbers, 
                                                             data_type='sample', 
                                                             data_root_path=sample_folder)
    ob_master_dict, ob_status_metadata = create_master_dict(list_run_numbers=list_ob_run_numbers, 
                                                         data_type='ob', 
                                                         data_root_path=ob_folder)
                                                             
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
    normalized_by_frame_number = (sample_status_metadata.all_frame_number_found and ob_status_metadata.all_frame_number_found)

    # combine all ob images
    ob_data_combined = combine_ob_images(ob_master_dict, use_proton_charge=normalized_by_proton_charge, use_frame_number=normalized_by_frame_number)
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
    for _sample_run_number in list_sample_run_numbers:
        logging.info(f"normalization of run {_sample_run_number}")
        if verbose:
            display(HTML(f"Normalization of run {_sample_run_number}"))

        _sample_data = np.array(sample_master_dict[_sample_run_number][MasterDictKeys.data], dtype=np.float32)

        if normalized_by_proton_charge:
            proton_charge = sample_master_dict[_sample_run_number][MasterDictKeys.proton_charge]
            _sample_data = _sample_data / proton_charge

        if normalized_by_frame_number:
            frame_number = sample_master_dict[_sample_run_number][MasterDictKeys.frame_number]
            _sample_data = _sample_data / frame_number

        _sample_data /= ob_data_combined

        normalized_data[_sample_run_number] = _sample_data

    logging.info(f"Normalization is done!")
    if verbose:
        display(HTML(f"Normalization is done!"))

    logging.info(f"Exporting normalized data to {output_folder} ...")
    if verbose:
        display(HTML(f"Exporting normalized data to {output_folder} ..."))

    # make up new output folder name
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

    logging.info(f"Exporting normalized data is done!")
    if verbose:
        display(HTML(f"Exporting normalized data is done!"))


def make_tiff(data=[], filename='', metadata=None):
    new_image = Image.fromarray(np.array(data))
    if metadata:
        new_image.save(filename, tiffinfo=metadata)
    else:
        new_image.save(filename)


def init_master_dict(list_run_numbers):
    master_dict = {}
    for run_number in list_run_numbers:
        master_dict[run_number] = {MasterDictKeys.nexus_path: None, 
                                   MasterDictKeys.frame_number: None, 
                                   MasterDictKeys.data_path: None, 
                                   MasterDictKeys.proton_charge: None,
                                   MasterDictKeys.matching_ob: [] ,
                                   MasterDictKeys.list_tif: [], 
                                   MasterDictKeys.data: None}

    return master_dict

def retrieve_root_nexus_full_path(sample_folder):
    clean_path = os.path.abspath(sample_folder)
    if clean_path[0] == "/":
        clean_path = clean_path[1:]

    path_splitted = clean_path.split("/")
    facility = path_splitted[0]
    instrument = path_splitted[1]
    ipts = path_splitted[2]

    return f"/{facility}/{instrument}/{ipts}/nexus/"


def update_dict_with_frame_number(master_dict):
    status_all_frame_number_found = True
    for _run_number in master_dict.keys():
        _nexus_path = master_dict[_run_number][MasterDictKeys.nexus_path]
        try:
            with h5py.File(_nexus_path, 'r') as hdf5_data:
                frame_number = hdf5_data['entry']['DASlogs']['BL10:Det:PIXELMAN:ACQ:NUM']['value'][:][-1]
        except KeyError:
            frame_number = None
            status_all_frame_number_found = False
        master_dict[_run_number][MasterDictKeys.frame_number] = frame_number
    return master_dict, status_all_frame_number_found


def update_dict_with_proton_charge(master_dict):
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
    

def update_dict_with_list_of_images(master_dict):
    for _run_number in master_dict.keys():
        list_tif = retrieve_list_of_tif(master_dict[_run_number][MasterDictKeys.data_path])
        master_dict[_run_number][MasterDictKeys.list_tif] = list_tif
    return master_dict


def get_list_run_number(data_folder):
    list_runs = glob.glob(os.path.join(data_folder, "Run_*"))
    list_run_number = [int(os.path.basename(run).split("_")[1]) for run in list_runs]
    return list_run_number


def update_dict_with_nexus_full_path(nexus_root_path, master_dict):
    """create dict of nexus path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.nexus_path] = os.path.join(nexus_root_path, f"VENUS_{run_number}.nxs.h5")
    return master_dict


def update_dict_with_data_full_path(data_root_path, master_dict):
    """create dict of data path for each run number"""
    for run_number in master_dict.keys():
        master_dict[run_number][MasterDictKeys.data_path] = os.path.join(data_root_path, f"Run_{run_number}")
    return master_dict


def create_master_dict(list_run_numbers=None, data_type="sample", data_root_path=None):
    logging.info(f"Create {data_type} master dict of runs: {list_run_numbers = }")

    status_metadata = StatusMetadata()

    nexus_root_path = retrieve_root_nexus_full_path(data_root_path)
    logging.info(f"{nexus_root_path =}")

    # retrieve metadata for each run number
    master_dict = init_master_dict(list_run_numbers)

    logging.info(f"updating with data full path!")
    master_dict = update_dict_with_data_full_path(data_root_path, master_dict)

    logging.info(f"updating with nexus full path!")
    master_dict = update_dict_with_nexus_full_path(nexus_root_path, master_dict)

    logging.info(f"updating with frame number!")
    master_dict, all_frame_number_found = update_dict_with_frame_number(master_dict)
    if not all_frame_number_found:
        status_metadata.all_frame_number_found = False
    logging.info(f"{master_dict = }")

    logging.info(f"updating with proton charge!")
    master_dict, all_proton_charge_found = update_dict_with_proton_charge(master_dict)
    if not all_proton_charge_found:
        status_metadata.all_proton_charge_found = False
    logging.info(f"{master_dict = }")

    logging.info(f"updating with list of images!")
    master_dict = update_dict_with_list_of_images(master_dict)

    return master_dict, status_metadata


def combine_ob_images(ob_master_dict,  use_proton_charge=False, use_frame_number=False):
    logging.info(f"Combining all open beam images and correcting by proton charge and frame number ...")
    full_ob_data_corrected = []

    for _ob_run_number in ob_master_dict.keys():
        logging.info(f"Combining ob# {_ob_run_number} ...")
        ob_data = np.array(ob_master_dict[_ob_run_number][MasterDictKeys.data], dtype=np.float32)

        if use_proton_charge:
            logging.info(f"\t -> Normalized by proton charge")
            proton_charge = ob_master_dict[_ob_run_number][MasterDictKeys.proton_charge]
            ob_data = ob_data / proton_charge

        if use_frame_number:
            logging.info(f"\t -> Normalized by frame number")
            frame_number = ob_master_dict[_ob_run_number][MasterDictKeys.frame_number]
            ob_data = ob_data / frame_number

        full_ob_data_corrected.append(ob_data)

    ob_data_combined = np.array(full_ob_data_corrected).mean(axis=0)

    # remove zeros
    ob_data_combined[ob_data_combined == 0] = np.NaN

    return ob_data_combined


if __name__ == '__main__':

    # sample_master_dict = {'run_number': {'nexus_path': 'path', 'frame_number': 'value', 'proton_charge': 'value', 'matching_ob': []}}

    parser = argparse.ArgumentParser(description="Normalized Timepix data with frame number and proton charge",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument("--sample", type=str, nargs=1, help="Path to the folder containing the sample data")
    parser.add_argument("--ob", type=str, nargs=1, help="Path to the folder containing the open beam data")
    parser.add_argument("--output", type=str, nargs=1, help="Path to the output folder", default="./")
    
    args = parser.parse_args()
    logging.info(f"{args = }")

    try:
        sample_folder = args.sample[0]
        if not os.path.exists(sample_folder):
            logging.info(f"sample folder {sample_folder} does not exist!")
            raise FileNotFoundError(f"Folder {sample_folder} does not exist!")
        else:
            logging.info(f"sample folder {sample_folder} located!")

    except (TypeError, FileNotFoundError):
        print("\n *** INPUT ERROR of sample folder! ***\n")
        print(parser.print_help())
        exit()
    
    try:
        ob_folder = args.ob[0]
        if not os.path.exists(ob_folder):
            logging.info(f"open beam folder {ob_folder} does not exist!")
            raise FileNotFoundError(f"Folder {ob_folder} does not exist!")
        else:
            logging.info(f"open beam folder {ob_folder} located!")

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

    normalization(sample_folder=sample_folder, ob_folder=ob_folder, output_folder=output_folder)

    print(f"Normalization is done! Check the log file {log_file_name} for more details!")
    print(f"Exported data to {output_folder}!")

    # sample = /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_Sample6_UA_H_Batteries_1_5_Angs_min_30Hz_5C
    # ob = /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_OB_for_UA_H_Batteries_1_5_Angs_min_30Hz_5C

    # full command to use to test code
    
    # source /opt/anaconda/etc/profile.d/conda.sh
    # conda activate ImagingReduction
    # > python normalization_for_timepix.py --sample /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_Sample6_UA_H_Batteries_1_5_Angs_min_30Hz_5C --ob /SNS/VENUS/IPTS-34808/shared/autoreduce/mcp/November17_OB_for_UA_H_Batteries_1_5_Angs_min_30Hz_5C --output /SNS/VENUS/IPTS-34808/shared/processed_data/jean_test