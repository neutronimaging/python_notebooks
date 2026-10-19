import argparse
import json
import logging
import os

import dxchange
import numpy as np
from __code._utilities.file import make_tiff
from __code._utilities.logger import setup_logging
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    apply_cylindrical_correction,
    replace_with_nans,
)
from scipy.ndimage import rotate
from tqdm import tqdm

setup_logging(basename_of_log_file="cylindrical_geometry_correction_cli")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform cylindrical geometry correction on white beam mode images."
    )
    parser.add_argument(
        "config_json_file",
        type=str,
        nargs=1,
        help="JSON config file created by cylindrical_geometry_correction_for_white_beam_data.ipynb notebook.",
    )
    args = parser.parse_args()

    config_json_file = args.config_json_file[0]
    with open(config_json_file) as f:
        config = json.load(f)

    output_folder = config.get("output_folder", None)
    if not output_folder:
        logging.error(
            "No output folder found in the config file. Please make sure the config file contains an 'output_folder' key with a valid folder path."
        )
        exit(1)

    list_of_files = config.get("list_of_images", [])
    if not list_of_files:
        logging.error(
            "No list of images found in the config file. Please make sure the config file contains a 'list_of_images' key with a list of image file paths."
        )
        exit(1)

    x0 = config["default_crop"]["x0"]
    y0 = config["default_crop"]["y0"]
    x1 = config["default_crop"]["x1"]
    y1 = config["default_crop"]["y1"]
    logging.info(f"Default crop values: x0={x0}, y0={y0}, x1={x1}, y1={y1}")

    c_disc = np.array(config["c_disc"])
    c_disc = c_disc[:, np.newaxis]

    logging.info(
        f"Loaded c_disc from config with shape {np.shape(c_disc)}, type(c_disc)={type(c_disc)}"
    )
    res_mask = np.array(config["res_mask"])
    logging.info(
        f"Loaded res_mask from config with shape {np.shape(res_mask)}, type(res_mask)={type(res_mask)}"
    )

    # process one file at a time
    for _file in tqdm(list_of_files):
        logging.info(f"Processing image: {os.path.basename(_file)}")

        # load the file
        data = np.array(dxchange.read_tiff(_file))
        logging.info(f"\tLoaded data shape: {data.shape}, dtype: {data.dtype}")

        # apply rotation
        rotation_angle = config["rotation_angle"]["angle"]
        rotation_90_flag = config["rotation_angle"]["rotate_90_flag"]
        logging.info(
            f"\tApplying rotation: rotation_90_flag={rotation_90_flag}, rotation_angle={rotation_angle}"
        )
        if rotation_90_flag:
            data = np.rot90(data)
        if rotation_angle != float(0):
            data = rotate(data, rotation_angle)
        logging.info(f"\tData shape after rotation: {data.shape}")

        # crop
        data = data[y0 : y1 + 1, x0 : x1 + 1]
        logging.info(f"\tData shape after cropping: {data.shape}")

        # detection of edges
        data = np.array([data])
        logging.info(f"\tData shape after adding batch dimension: {data.shape}")

        data = replace_with_nans(data)
        logging.info(f"\tData shape after replacing with NaNs: {data.shape}")

        integrated_data = np.sum(data, axis=0)
        logging.info(f"\tIntegrated data shape: {integrated_data.shape}")

        # detection_config = DetectionConfig()

        # geometry, diagnostics = detect_cylindrical_boundary(integrated_data, detection_config)

        # res = calculate_cylindrical_chord_map(image_shape=integrated_data.shape,
        #                                       center_x=geometry.center_x,
        #                                       top_edge=geometry.top_edge,
        #                                       bottom_edge=geometry.bottom_edge,
        #                                       radius=geometry.radius,
        #                                       is_hollow=False,
        #                                       outside_fill="nan",
        #                                       edge_epsilon=0.0)

        # mu_disc, mu_iter, c_disc = compute_correction_map_factor(data,
        #                                                          geometry,
        #                                                          res)

        # logging.info(f"\t{c_disc =} and {c_disc.shape =} and {c_disc.dtype =}")

        # logging.info(f"\t{res.mask =} and {res.mask.shape =} and {res.mask.dtype =}")

        hyperspectral_stack = np.swapaxes(data, 0, 2)
        hyperspectral_stack = np.swapaxes(hyperspectral_stack, 0, 1)  # "H, W, L or TOF"

        # apply correction
        Tcorr = apply_cylindrical_correction(
            T_yxl=hyperspectral_stack, C_xl=c_disc, mask_yx=res_mask, copy=True
        )
        _intermediate = np.swapaxes(Tcorr, 0, 2)
        corrected_data = np.swapaxes(_intermediate, 1, 2)  # "nbr, W, H"

        # export to output folder
        base_file_name = os.path.basename(_file)
        output_file = os.path.join(output_folder, f"{base_file_name}")
        make_tiff(filename=output_file, data=corrected_data[0])
        logging.info(f"Saved corrected data to: {output_file}")
