import glob
import logging
import os
from pathlib import Path

from __code._utilities.nexus import (
    extract_acquisition_time_from_nexus,
    extract_proton_charge_from_nexus,
    retrieve_file_path_from_nexus,
)
from __code.normalization_white_beam_at_venus import DataDict


def extract_run_number_from_file_name(file_name: str) -> int | None:
    """
    Extract the run number from the given file name.

    Parameters
    ----------
    file_name : str
        The name of the file from which to extract the run number.

    Returns
    -------
        int or None
        The extracted run number if found, otherwise None.
    """
    base_name = os.path.basename(file_name)

    split_name = base_name.split("_Run_")
    part2 = split_name[1] if len(split_name) > 1 else None
    if part2 is None:
        return None

    part2_split = part2.split("_")
    run_number_str = part2_split[0] if len(part2_split) > 0 else None
    if run_number_str is None:
        return None

    return int(run_number_str) if run_number_str.isdigit() else None


def extract_metadata(
    run_number=None, nexus_path=None, ipts_path=None, instrument=None
) -> dict:
    """
    Extract various metadata from the Nexus file
    Parameters
    ----------
    run_number : int, optional
        The run number for which to extract metadata. If None, the function will return an empty dictionary.
    nexus_path : str, optional
        The path to the Nexus file. If None, the function will return an empty dictionary.
    ipts_path : str, optional
        The path to the IPTS folder. If None, the function will return an empty dictionary.
    instrument : str, optional
        The name of the instrument. If None, the function will return an empty dictionary.

    return {'full_image_path': '', 'acquisition_time': '', 'proton_charge': ''}
    """

    logging.info(f"Extracting metadata for run number: {run_number}")

    _dict = DataDict()

    if run_number is None:
        raise ValueError("Run number must be provided")

    # retrieve the path from the NeXus file
    nexus_path, file_path = retrieve_file_path_from_nexus(
        nexus_folder_path=Path(nexus_path), instrument=instrument, run_number=run_number
    )
    logging.info(f"\tNexus path: {nexus_path}")
    _dict.nexus_path = nexus_path

    if os.path.exists(nexus_path):
        logging.info(f"\tNexus file found for run number {run_number}")
        # retrieving proton charge and acquisition time from the NeXus file
        _dict.proton_charge = extract_proton_charge_from_nexus(nexus_path)
        _dict.acquisition_time = extract_acquisition_time_from_nexus(nexus_path)

    logging.info(f"\tFile path retrieved from NeXus: {file_path}")
    full_path = os.path.join(ipts_path, file_path) if file_path is not None else None
    logging.info(f"\t{full_path =}")
    path_of_that_run_in_that_file_path = glob.glob(
        os.path.join(full_path, f"*_Run_{run_number}_*")
    )

    path_to_return = (
        path_of_that_run_in_that_file_path[0]
        if len(path_of_that_run_in_that_file_path) > 0
        else None
    )
    _dict.full_path = path_to_return

    if file_path is None:
        raise ValueError(f"No full path file found for run number {run_number}")

    logging.info(f"\t{path_of_that_run_in_that_file_path = }")
    return _dict
