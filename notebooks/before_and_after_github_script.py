import argparse
import os
import glob

from __code.file_handler import read_ascii, make_ascii_file_from_string

# this script will convert the notebooks to .py before pushing to github and the .py files back to
# notebooks after pulling from github

parser = argparse.ArgumentParser(description='Before Push or After Pull from GitHub')
parser.add_argument('-b', '--before_push', action="store_true", help='Convert all .ipynb to .py in converted_notebooks folder')
parser.add_argument('-a', '--after_pull', action="store_true", help='Convert all .py from converted_notebooks folder to .ipynb')
parser.add_argument('-d', '--use_debugging_mode', action="store_true", help='Change the debugging mode on/off')

def run():

    args = parser.parse_args()
    _top_path = os.path.dirname(__file__)
    if args.before_push:
        list_notebooks = glob.glob('*.ipynb')
        list_users_notebooks = glob.glob('users_notebooks/*.ipynb')
        list_notebooks += list_users_notebooks
        list_notebooks.sort()

        print("Cleaning ...")
        for _notebook in list_notebooks:
            os.system('nbstripout {}'.format(_notebook))
            print(" > {}".format(_notebook))

        list_notebooks_after = glob.glob('*.ipynb')
        list_users_notebooks_after = glob.glob('users_notebooks/*.ipynb')
        list_notebooks_after += list_users_notebooks_after
        list_notebooks_after.sort()

        if len(list_notebooks) == len(list_notebooks_after):
            print(" Cleaning Result:  OK!")
        else:
            print(" Cleaning Result: WARNING!")
            for _file in list_notebooks:
                if not (_file in list_notebooks_after):
                    print(" Missing File: {}".format(_file))

        os.system('jupytext --to converted_notebooks//py *.ipynb')
        os.system('jupytext --to converted_notebooks//py users_notebooks/*.ipynb')

    elif args.after_pull:
        os.system('jupytext --to ipynb converted_notebooks/*.py')

    # turn debugging flag ON/OFF
    print("---> debugging mode is {}".format(args.use_debugging_mode))
    if args.use_debugging_mode:
        print("Turning Debugging Mode ON!")
    else:
        print("Turning Debugging Mode OFF!")

    config_file = os.path.join(_top_path, '__code/config.py')
    _config_file_contain = read_ascii(config_file)
    _parse = _config_file_contain.split('\n')
    _parse[0] = 'debugging = {}'.format(args.use_debugging_mode)
    _new_contain = '\n'.join(_parse)

    make_ascii_file_from_string(text=_new_contain, filename=config_file)


if __name__ == '__main__':
    run()
