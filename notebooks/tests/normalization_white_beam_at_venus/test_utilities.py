import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../__code/normalization_white_beam_at_venus'))
from utilities import extract_run_number_from_file_name
import pytest

class TestUtilities:
   
    def test_extract_run_number_from_file_name(self):
        
        file_name = "/path/to/file/sample_Run_12345_data.tiff"
        expected_run_number = 12345
        returned_run_number = extract_run_number_from_file_name(None, file_name)  # Pass None for self parameter
        assert returned_run_number == expected_run_number, f"Expected {expected_run_number}, but got {returned_run_number}"
        
        file_name = "/SNS/VENUS/IPTS-25778/images/ikonx/raw/radiography/20260227_no_sample_andor_test_4_000s_0_700AngsMin/20260227_Run_15242_no_sample.tiff"
        expected_run_number = 15242
        returned_run_number = extract_run_number_from_file_name(None, file_name)  # Pass None for self parameter
        assert returned_run_number == expected_run_number, f"Expected {expected_run_number}, but got {returned_run_number}"
