import logging
from pathlib import Path

import h5py


def extract_data_file_path_from_nexus(nexus_file_path):
    """
    Extract the file path from a Nexus file path string.

    :param nexus_file_path: str, the Nexus file path
    :return: str, the extracted file path
    """
    logging.info(f"Extracting file path from NeXus file: {nexus_file_path}")
    with h5py.File(str(nexus_file_path), "r") as hdf5_data:
        list_file_path = hdf5_data["entry"]["DASlogs"]["BL10:Exp:IM:ImageFilePath"]["value"][:]
        logging.info(f"\t{list_file_path} = ")
        file_path = list_file_path[-1][0].decode("utf-8")
        file_path = file_path.strip()
        logging.info(f"\t{file_path = }")
    return Path(file_path)


def extract_file_path_from_nexus(nexus_file_path):
    return extract_data_file_path_from_nexus(nexus_file_path)


def extract_proton_charge_from_nexus(nexus_path):
    """
    Extract the proton charge from the NeXus file.
    This function should be implemented to read the NeXus file and extract the proton charge.
    """
    # Placeholder implementation, replace with actual logic to read NeXus file
    if nexus_path is None:
        return None

    try:
        with h5py.File(nexus_path, 'r') as hdf5_data:
            proton_charge = hdf5_data["entry"]["proton_charge"][0]
            return proton_charge
    except FileNotFoundError:
        return None


def extract_acquisition_time_from_nexus( nexus_path):
    """
    Extract the acquisition time from the NeXus file.
    This function should be implemented to read the NeXus file and extract the acquisition time.
    """
    if nexus_path is None:
        return None

    try:
        with h5py.File(nexus_path, 'r') as hdf5_data:
            duration = float(hdf5_data['entry']['duration'][0])
            return duration
    except FileNotFoundError:
        return None
    
    
def retrieve_file_path_from_nexus(nexus_folder_path=str, instrument=str, run_number=int):
    """
    Retrieve the full path to the NeXus file for the given run number.
    This function should be implemented to read the NeXus file and extract the path.
    return the nexus path and the file path of the image on the filesystem
    """
    # Placeholder implementation, replace with actual logic to read NeXus file
    nexus_file_path = Path(nexus_folder_path) / f"{instrument.upper()}_{run_number}.nxs.h5"
    if nexus_file_path.exists():
        return nexus_file_path, extract_data_file_path_from_nexus(nexus_file_path)
    else:
        return None, None
