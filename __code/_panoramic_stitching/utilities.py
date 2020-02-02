class Utilities:

    def __init__(self, parent=None):
        self.parent = parent

    def get_roi(self, full_file_name=''):
        master_dict = self.parent.master_dict[full_file_name]['reference_roi']
        x0 = master_dict['x0']
        y0 = master_dict['y0']
        width = master_dict['width']
        height = master_dict['height']
        return [x0, y0, width, height]
