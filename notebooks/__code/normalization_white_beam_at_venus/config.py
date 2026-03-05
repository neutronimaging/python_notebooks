from __code.resonance_fitting import DetectorType


class DEBUG_DATA:
    ipts = "IPTS-25778"
    working_dir = f"/SNS/VENUS/{ipts}"
    output_folder = f"{working_dir}/shared/processed_data/jean_test"
    sample_runs_selected = ["Run_15242", "Run_15241", "Run_15243"]
    ob_runs_selected = ["Run_14640", "Run_14641"]
    dc_runs_selected = []
    roi = [154, 156, 180, 17]
    container_roi = [150, 150, 40, 40]
    detector_type = DetectorType.tpx1  # timepix1 or timepix3

## timepix3
# class DEBUG_DATA:
#     ipts = "IPTS-35167"
#     working_dir = f"/SNS/VENUS/{ipts}"
#     autoreduce_dir = f"/SNS/VENUS/{ipts}/shared/autoreduce/mcp/images"
#     output_folder = f"{working_dir}/shared/processed_data/jean_test"
#     sample_runs_selected = ["Run_14808"]
#     ob_runs_selected = ["Run_14809"]
#     dc_runs_selected = []
#     roi = [154, 156, 180, 17]
#     container_roi = [150, 150, 40, 40]
#     detector_type = DetectorType.tpx3  # timepix1 or timepix3


timepix1_config = {
    "chip1": {"xoffset": 2.4, "yoffset": 1, "description": "top right chip"},
    "chip2": {"xoffset": 0, "yoffset": 0, "description": "top left and reference chip"},
    "chip3": {"xoffset": 0, "yoffset": 1, "description": "bottom left chip"},
    "chip4": {"xoffset": 2.3, "yoffset": 2.3, "description": "bottom right chip"},
}

timepix3_config = {
    "chip1": {"xoffset": 2.4, "yoffset": 1, "description": "top right chip"},
    "chip2": {"xoffset": 0, "yoffset": 0, "description": "top left and reference chip"},
    "chip3": {"xoffset": 0, "yoffset": 1, "description": "bottom left chip"},
    "chip4": {"xoffset": 2.3, "yoffset": 2.3, "description": "bottom right chip"},
}
