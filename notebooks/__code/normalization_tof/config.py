class DEBUG_DATA:
    ipts = "IPTS-35742"
    working_dir = f"/SNS/VENUS/{ipts}/shared/"
    autoreduce_dir = f"/SNS/VENUS/{ipts}/shared/autoreduce/mcp/images"
    output_folder = f"{working_dir}/shared/processed_data/jean_test"
    sample_runs_selected = ["Run_13454"]
    ob_runs_selected = ["Run_13449"]
    dc_runs_selected = []
    roi = [154, 156, 180, 17]

timepix1_config = {
    "chip1": {"xoffset": 1, "yoffset": 1, "description": "top right chip"},
    "chip2": {"xoffset": 0, "yoffset": 0, "description": "top left and reference chip"},
    "chip3": {"xoffset": 0, "yoffset": 1, "description": "bottom left chip"},
    "chip4": {"xoffset": 1, "yoffset": 2, "description": "bottom right chip"},
}

timepix3_config = {
    "chip1": {"xoffset": 0, "yoffset": 0, "description": "top right chip"},
    "chip2": {"xoffset": 0, "yoffset": 0, "description": "top left and reference chip"},
    "chip3": {"xoffset": 0, "yoffset": 0, "description": "bottom left chip"},
    "chip4": {"xoffset": 0, "yoffset": 0, "description": "bottom right chip"},
}
