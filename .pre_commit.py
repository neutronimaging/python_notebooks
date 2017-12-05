import os
import glob

# this will clean up all the ipynb files by running the nbstripout program

_file_path = os.path.dirname(__file__)
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
    for _file in list_notebook:
        if not (_file in list_notebooks_after):
            print(" Missing File: {}".format(_file))


