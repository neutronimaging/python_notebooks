class FittingRegions:

    high_lambda = "high_lambda"
    low_lambda = "low_lambda"
    bragg_peak = "bragg_peak"


class DefaultFittingParameters:

    a0 = 1
    b0 = 1
    ahkl = 1
    bhkl = 1
    lambdahkl = 5e-7
    tau = 1
    sigma = 0.01


class JSONKeys:

    dSD_m = "distance source detector in m"
    infos = "infos"
    input_nexus_filename = "input nexus filename"
    offset_micros = "offset in micros"
    time_shift = "time shift"
    element = "element"

    left_range = "left_range"
    right_range = "right_range"
    left_edge = "left_edge"
    right_edge = "right_edge"

    rois_selected = "ROIs selected"
    x0 = "x0"
    y0 = "y0"
    x1 = "x1"
    y1 = "y1"

    fitting_parameters = "fitting parameters"
    a0 = "a0"
    b0 = "b0"
    ahkl = "ahkl"
    bhkl = "bhkl"
    lambdahkl = "lambdahkl"
    tau = "tau"
    sigma = "sigma"


LIST_ELEMENTS = ['Ni', 'Ta', 'Al']
LIST_ELEMENTS_SUPPORTED = ['Ni', 'Al']
