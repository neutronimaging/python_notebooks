import collections


def key_path_exists_in_dictionary(dictionary=None, tree_key=None):
    """this method checks if full key path in the dictionary exists"""
    top_dictionary = dictionary
    for _key in tree_key:
        if top_dictionary.get(_key, None) is None:
            return False
        top_dictionary = top_dictionary.get(_key)
    return True


def combine_dictionaries(master_dictionary={}, servant_dictionary={}):
    new_master_dictionary = collections.OrderedDict()
    for _key in master_dictionary.keys():
        _servant_key = master_dictionary[_key]['filename']
        _dict1 = master_dictionary[_key]
        _dict2 = servant_dictionary[_servant_key]
        _dict3 = {**_dict1, **_dict2}
        new_master_dictionary[_key] = _dict3
    return new_master_dictionary
