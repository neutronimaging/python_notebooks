import logging
from pathlib import Path

import h5py


def extract_file_path_from_nexus(nexus_file_path):
    """
    Extract the file path from a Nexus file path string.

    :param nexus_file_path: str, the Nexus file path
    :return: str, the extracted file path
    """
    logging.info(f"Extracting file path from NeXus file: {nexus_file_path}")
    with h5py.File(str(nexus_file_path), "r") as hdf5_data:
        list_file_path = hdf5_data["entry"]["DASlogs"]["BL10:Exp:IM:ImageFilePath"][
            "value"
        ][:]
        logging.info(f"\t{list_file_path} = ")
        file_path = list_file_path[-1][0].decode("utf-8")
        file_path = file_path.strip()
        logging.info(f"\t{file_path = }")
    return Path(file_path)
