import argparse
import os
import glob

from __code.file_handler import read_ascii, make_ascii_file_from_string

# this will clean up all the ipynb files by running the nbstripout program
# in the specified folder

parser = argparse.ArgumentParser(description='Preparing notebooks for deploymenet to analysis machine')
parser.add_argument('-i', '--input', help='Input folder to clean.', type=str)

def run():

    args = parser.parse_args()
    _file_path = args.input

    _top_path = os.path.dirname(__file__)
    list_notebooks = glob.glob(os.path.abspath(_file_path) + '/*.ipynb')
    list_notebooks.sort()

    print("Cleaning ...")
    for _notebook in list_notebooks:
        os.system('nbstripout {}'.format(_notebook))
        print(" > {}".format(_notebook))

    list_notebooks_after = glob.glob(os.path.abspath(_file_path) + '/*.ipynb')
    list_notebooks_after.sort()

    if len(list_notebooks) == len(list_notebooks_after):
        print(" Cleaning Result:  OK!")
    else:
        print(" Cleaning Result: WARNNG!")
        for _file in list_notebooks:
            if not (_file in list_notebooks_after):
                print(" Missing File: {}".format(_file))

    # turn debugging flag OFF
    print("Turning Off Debugging Mode!")
    config_file = os.path.join(_top_path, '__code/config.py')
    _config_file_contain = read_ascii(config_file)
    _parse = _config_file_contain.split('\n')
    _parse[0] = 'debugging = False'
    _new_contain = '\n'.join(_parse)

    make_ascii_file_from_string(text=_new_contain, filename=config_file)


if __name__ == '__main__':
    run()

