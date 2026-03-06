import argparse
import json
import logging
from turtle import setup

from __code._utilities.logger import setup_logging
setup_logging(basename_of_log_file="cylindrical_geometry_correction_cli")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Perform cylindrical geometry correction on white beam mode images.")
    parser.add_argument('config_json_file', type=str, nargs=1, help="JSON config file created by cylindrical_geometry_correction_for_white_beam_data.ipynb notebook.")
    args = parser.parse_args()
    
    config_json_file = args.config_json_file[0]
    with open(config_json_file) as f:
        config = json.load(f)
        
    