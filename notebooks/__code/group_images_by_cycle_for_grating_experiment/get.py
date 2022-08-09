import os


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def default_metadata_selected(self):
        config = self.parent.config
        list_metadata = self.parent.list_metadata

        value_inner, value2 = "", ""

        metadata_inner = config['metadata_inner']
        for _entry in list_metadata:
            if f"{metadata_inner['key']} -> {metadata_inner['name']}:" in _entry:
                value_inner = _entry

        metadata_outer = config['metadata_outer']
        for _entry in list_metadata:
            if f"{metadata_outer['key']} -> {metadata_outer['name']}:" in _entry:
                value_outer = _entry

        return value_inner, value_outer

    def list_of_old_files_fullname(self, index):
        list_entries = self.parent.dictionary_of_groups_sorted[index]
        list_files = []
        for _key in list_entries.keys():
            list_files.append(list_entries[_key])

        return list_files

    def list_of_files_basename_only(self, index):
        list_entries = self.parent.dictionary_of_groups_sorted[index]
        list_files = []
        for _key in list_entries.keys():
            _short_file_name = [os.path.basename(_file) for _file in list_entries[_key]]
            _str_file_name = ", ".join(_short_file_name)
            list_files.append(_str_file_name)
        return list_files

    def list_of_new_files_basename_only(self, index):
        """return the list of new file names for that group"""
        list_files = self.parent.dictionary_of_groups_new_names[index]
        short_list_files = [os.path.basename(_file) for _file in list_files]
        return short_list_files
