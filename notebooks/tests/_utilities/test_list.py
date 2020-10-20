from __code._utilities import list


def test_are_those_two_lists_identical_within_tolerance():
    list1 = [1, 2]
    list2 = [1, 2, 3]
    assert not list.are_those_two_lists_identical_within_tolerance(list1, list2)

    list1 = [1, 2]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list1)

    list1 = [1, 2]
    list2 = [1, 2]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list2)

    list1 = [1, 2]
    list2 = [1, 2.0001]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list2)

    list1 = [1, 2, 3]
    list2 = [1, 2.0001, 3]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list2)

    list1 = [1, 2, 3]
    list2 = [1, 2.0001, 4]
    assert not list.are_those_two_lists_identical_within_tolerance(list1, list2)

    list1 = [1, 2, 3]
    list2 = [1, 2.1, 3]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list2, tolerance=0.2)

    list1 = [1, 2, 3]
    list2 = [1, 2.1, 3]
    assert not list.are_those_two_lists_identical_within_tolerance(list1, list2, tolerance=0.1)

    list1 = [1, 2, 3, 4, 5, 6, 7]
    list2 = [1, 2.1, 3, 4.1, 5, 6.1, 7]
    assert list.are_those_two_lists_identical_within_tolerance(list1, list2, tolerance=0.15)

def test_are_those_two_lists_of_lists_identical_within_tolerance():
    list1 = [[1, 2]]
    list2 = [[1, 2], [3, 4]]
    assert not list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list2)

    list1 = [[1, 2], [3, 4]]
    assert list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list1)

    list1 = [[1, 2], [3, 4]]
    list2 = [[1, 2], [3, 4]]
    assert list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list2)

    list1 = [[1, 2], [3, 4], [5, 6, 7]]
    list2 = [[1, 2], [3, 4], [5, 6, 7]]
    assert list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list2)

    list1 = [[1, 2.1], [3, 4], [5, 6.1, 7]]
    list2 = [[1, 2], [3, 4.1], [5, 6, 7]]
    assert list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list2, tolerance=0.15)

    list1 = [[1, 2.1], [3, 4], [5, 6.1, 7]]
    list2 = [[1, 2], [3, 4.2], [5, 6, 7]]
    assert not list.are_those_two_lists_of_lists_identical_within_tolerance(list1, list2, tolerance=0.15)
