import numpy as np
from IPython.core.display import HTML


def get_beginning_common_part_of_string_from_list(list_of_text=None, filename_spacer='_'):
    """This method returns the continuous part of a string, from the beginning, that can be found
    in all string provided. The match will stop before the last filename_spacer

    for example:
    list_of_text = ['abc_000.txt', 'abc_001.txt', 'abc_002.txt']
    the method will return 'abc_'
    """
    if list_of_text is None:
        raise ValueError("Please provide a list of string!")

    split_list_of_text = [text.split(filename_spacer) for text in list_of_text]
    split_list_of_text = np.array(split_list_of_text)

    common_part = []
    [_, nbr_argument] = split_list_of_text.shape
    for _index in np.arange(nbr_argument):
        _array = split_list_of_text[:, _index]
        _set = set(_array)
        if len(_set) > 1:
            break
        common_part.append(list(_set)[0])

    return filename_spacer.join(common_part)


def format_html_message(pre_message='', spacer=':', message='', is_error=False):
    if is_error:
        pre_message_color = 'red'
        message_color = 'red'
    else:
        pre_message_color = 'blue'
        message_color = 'green'
    return HTML('<span style="font-size: 15px; color:' + pre_message_color + '">' + pre_message + spacer +
                '</span>' +
                 '<span style="font-size: 15px; color:' + message_color + '">' + message + '</span>')
