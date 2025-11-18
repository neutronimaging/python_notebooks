class DEBUG_DATA:
    ipts = "IPTS-35407"
    working_dir = f"/SNS/VENUS/{ipts}"
    autoreduce_dir = f"/SNS/VENUS/{ipts}/shared/autoreduce/mcp/images"
    output_folder = f"{working_dir}/shared/processed_data/jean"
    sample_runs_selected = ["Run_13083"]
    ob_runs_selected = ["Run_13082"]
    dc_runs_selected = ["Run_13081"]
    isotope_element = "Hf"


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
