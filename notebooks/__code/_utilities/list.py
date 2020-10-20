import numpy as np


def are_those_two_list_identical_within_tolerance(list1, list2, tolerance=0.01):
    """
    check that two lists of float/int are identical within the tolerenace given
    :param list1:
    :param list2:
    :param tolerance:
    :return:
    """

    if len(list1) != len(list2):
        return False

    if list1 == list2:
        return True

    for item1, item2 in zip(list1, list2):
        if not np.abs(item1 - item2) <= tolerance:
            return False

    return True
