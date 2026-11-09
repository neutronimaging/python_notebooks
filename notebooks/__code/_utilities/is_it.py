from pathlib import Path


def is_it_a_folder(path):
    return Path(path).is_dir()


def is_it_a_file(path):
    return Path(path).is_file()
