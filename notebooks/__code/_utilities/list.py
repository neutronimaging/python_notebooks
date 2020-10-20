import numpy as np


def are_those_two_lists_identical_within_tolerance(list1, list2, tolerance=0.01):
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
        if not np.abs(np.float(item1) - np.float(item2)) <= tolerance:
            return False

    return True

def are_those_two_lists_of_lists_identical_within_tolerance(list1, list2, tolerance=0.01):
    """
    check that 2 lists composed of lists are identical

    :param list1:
    :param list2:
    :param tolerance:
    :return:
    """
    if len(list1) != len(list2):
        return False

    if list1 == list2:
        return True

    for list_item1, list_item2 in zip(list1, list2):
        if not are_those_two_lists_identical_within_tolerance(list_item1, list_item2, tolerance=tolerance):
            return False

    return True