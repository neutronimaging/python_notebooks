import os
import glob

# this will clean up all the ipynb files by running the nbstripout program

_file_path = os.path.dirname(__file__)
list_notebooks = glob.glob(os.path.abspath(_file_path) + '/*.ipynb')

print("Cleaned ...")
for _notebook in list_notebooks:
    os.system('nbstripout {}'.format(_notebook))
    print(" > {}".format(_notebook))


