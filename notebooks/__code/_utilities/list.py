import numpy as np


def are_those_two_lists_identical_within_tolerance(list1, list2, tolerance=0.01):
    """
    check that two lists of float/int are identical within the tolerenace given
    :param list1: list
    :param list2: list
    :param tolerance:
    :return:
    """
    if (not (type(list1) == list)) or (not (type(list2) == list)):
        raise TypeError("first 2 parameters passed should be list!")

    if len(list1) != len(list2):
        return False

    if list1 == list2:
        return True

    for item1, item2 in zip(list1, list2, strict=False):
        if not np.abs(float(item1) - float(item2)) <= tolerance:
            return False

    return True


def are_those_two_lists_of_lists_identical_within_tolerance(
    list1, list2, tolerance=0.01
):
    """
    check that 2 lists composed of lists are identical

    :param list1: list of lists
    :param list2: list of lists
    :param tolerance:
    :return:
    """
    if (not (type(list1) == list)) or (not (type(list2) == list)):
        raise TypeError("first 2 parameters passed should be list!")

    if len(list1) != len(list2):
        return False

    if list1 == list2:
        return True

    for list_item1, list_item2 in zip(list1, list2, strict=False):
        if not are_those_two_lists_identical_within_tolerance(
            list_item1, list_item2, tolerance=tolerance
        ):
            return False

    return True


def is_this_list_already_in_those_lists_within_tolerance(list1, list2, tolerance=0.01):
    """
    checking that the first list passed in is already in the list of lists of list2 within the tolerance given

    :param list1: list
    :param list2: list of lists
    :param tolerance: float
    :return:
    """
    if (not (type(list1) == list)) or (not (type(list2) == list)):
        raise TypeError(
            "First argument should be a list of floats, second argument a list of lists"
        )

    for target_list in list2:
        if are_those_two_lists_identical_within_tolerance(
            list1, target_list, tolerance=tolerance
        ):
            return True

    return False


def extract_list_of_runs_from_string(string):
    """
    extracting a list of runs from a string
    e.g. "1234, 1255-1258" -> [1234, 1255, 1256, 1257, 1258]

    :param string: str
    """
    if not isinstance(string, str):
        raise TypeError("The parameter passed should be a string")

    list_of_runs = []
    list_of_items = string.split(",")
    for item in list_of_items:
        item = item.strip()
        if "-" in item:
            limits = item.split("-")
            if len(limits) != 2:
                raise ValueError(f"Wrong format for the range of runs: {item}")
            try:
                start = int(limits[0])
                end = int(limits[1])
            except Exception:
                raise ValueError(f"Wrong format for the range of runs: {item}")

            if start >= end:
                raise ValueError(f"Wrong format for the range of runs: {item}")

            list_of_runs += list(range(start, end + 1))
        else:
            try:
                run = int(item)
            except Exception:
                raise ValueError(f"Wrong format for the run number: {item}")
            list_of_runs.append(run)

    # removing duplicates and sorting the list
    list_of_runs = list(set(list_of_runs))
    list_of_runs.sort()

    return list_of_runs
