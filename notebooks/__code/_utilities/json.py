import json
import os


def load_json(json_file_name):
    if not os.path.exists(json_file_name):
        return None

    with open(json_file_name) as json_file:
        data = json.load(json_file)

    return data


def save_json(json_file_name, json_dictionary=None):
    with open(json_file_name, 'w') as outfile:
        json.dump(json_dictionary, outfile)
