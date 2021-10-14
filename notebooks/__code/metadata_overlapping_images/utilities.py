import re

from . import LIST_FUNNY_CHARACTERS


def string_cleaning(first_part_of_string_to_remove="", last_part_of_string_to_remove="", string_to_clean=""):
    first_part_of_string_to_remove = first_part_of_string_to_remove
    _clean_first_part = ""
    for _c in first_part_of_string_to_remove:
        if _c in LIST_FUNNY_CHARACTERS:
            _clean_first_part += "\{}".format(_c)
        else:
            _clean_first_part += "{}".format(_c)

    last_part_of_string_to_remove = last_part_of_string_to_remove
    _clean_second_part = ""
    for _c in last_part_of_string_to_remove:
        if _c in LIST_FUNNY_CHARACTERS:
            _clean_second_part += "\{}".format(_c)
        else:
            _clean_second_part += "{}".format(_c)

    regular_expr = r"{}(.*){}".format(_clean_first_part, _clean_second_part)

    m = re.match(regular_expr, str(string_to_clean))
    if m and m.group(1):
        _new_str = m.group(1)
        return _new_str

    return "N/A"


def linear_operation(input_parameter="", math_1="", value_1="", math_2="", value_2=""):

    if is_linear_operation_valid(input_parameter=input_parameter,
                                 value_1=value_1,
                                 value_2=value_2):

        operation_to_eval = f"{input_parameter}"
        if value_1:
            operation_to_eval += f" {math_1} {float(value_1)}"
        if value_2:
            operation_to_eval += f" {math_2} {float(value_2)}"

        result = eval(operation_to_eval)
        return result

    else:
        return ""


def is_linear_operation_valid(input_parameter="", value_1="", value_2=""):

    def is_error_in_operation(value):
        operation = str(value.strip())
        if operation:
            try:
                float(operation)
            except ValueError:
                return True
        return False

    if (not is_error_in_operation(value_1)) and \
        (not is_error_in_operation(value_2)) and \
        (not is_error_in_operation(input_parameter)):
        return True

    return False
