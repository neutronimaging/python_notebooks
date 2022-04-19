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
