from pathlib import Path


autoreduce_dir = {
    "VENUS": ["/SNS/VENUS/", "/shared/autoreduce/mcp/images"],
    "SNAP": ["/SNS/SNAP/", "/shared/autoreduce/mcp/"],
}

# shared_dir = {'VENUS': ["/SNS/VENUS/", "/shared/",],
#               'SNAP': ["/SNS/SNAP/", "/shared/",]}

distance_source_detector_m = {
    "VENUS": 25.0,  # in meters
    "SNAP": 14.0,  # in meters
}


class DetectorType:
    tpx1_legacy = "tpx1 - old naming convention (until July 2025)"
    tpx1 = "tpx1 - new naming convention (from August 2025)"
    tpx3 = "tpx3"


raw_dir = {
    "VENUS": {
        DetectorType.tpx1_legacy: ["/SNS/VENUS/", "images/mcp/images/"],
        DetectorType.tpx1: ["/SNS/VENUS/", "images/tpx1/"],
        DetectorType.tpx3: ["/SNS/VENUS/", ""],
    },
    "SNAP": {
        DetectorType.tpx1_legacy: ["/SNS/SNAP/", "images/mcp/"],
    },
}


autoreduce_dir = {
    "VENUS": {
        DetectorType.tpx1_legacy: ["/SNS/VENUS/", "shared/autoreduce/mcp/images/"],
        DetectorType.tpx1: ["/SNS/VENUS/", "shared/autoreduce/images/tpx1/"],
        DetectorType.tpx3: ["/SNS/VENUS/", "images/tpx3/"],
    },
    "SNAP": {
        DetectorType.tpx1_legacy: ["/SNS/SNAP/", "images/mcp/"],
    },
}

VENUS_RES_FUNC=Path("/SNS/VENUS/shared/instrument/resonance/_fts_bl10_0p5meV_1keV_25pts.txt")
SAMMY_EXE_PATH=Path("/SNS/software/sammy/bin/sammy")

class Parent:

    def __init__(self, parent=None):
        self.parent = parent
        