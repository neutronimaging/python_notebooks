import os
from os.path import expanduser

from __code._utilities.parent import Parent


class Get(Parent):

    @staticmethod
    def log_file_name(log_file_name):
        full_log_file_name = Get.full_home_file_name(log_file_name)
        return full_log_file_name

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name
