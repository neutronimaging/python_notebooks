import os


class Hdf5Handler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self, filename=None):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist!")
