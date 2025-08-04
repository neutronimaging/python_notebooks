from __future__ import print_function

requirements = [
    "jupyter",
    "matplotlib",
    "astropy",
    "neunorm",
    "pillow",
    "scipy",
    "scikit-image",
    "numpy",
    "pyoncat",
    "tifffile",
    "qtpy",
]

import_result = {p: False for p in requirements}

print("Checking requirements for Jupyter Imaging notebooks")

for package in requirements:
    try:
        __import__(package)
        import_result[package] = True
    except ImportError:
        pass

success = all(import_result.values())

version_check_packages = {
    "numpy": "1.15.2",
    "jupyter": "4.4.0",
    "matplotlib": "3.0.0",
    "astropy": "3.0.4",
    "NeuNorm": "1.4.3",
    "Pillow": "5.2.0",
    "scipy": "1.1.0",
    "scikit-image": "0.14.0",
    "ipywidgets": "7.4.1",
    "pandas": "0.23.4",
    "plotly": "3.2.1",
    "pyqtgraph": "0.10.0",
    "sectorizedradialprofile": "",
    "pyoncat": "1.0",
    "oauthlib": "3.0.1",
    "tifffile": "2019.7.26.2",
    "qtpy": "1.9.0",
}

if success:
    print("All required packages installed")
else:
    print(
        "Please install these missing packages to be able to run the Imaging Notebooks."
    )
    missing = [k for k, v in import_result.items() if not v]
    print("\t" + "\n\t".join(missing))

print(
    "Checking version numbers of these packages: ",
    ", ".join(version_check_packages.keys()),
)


def version_checker(package_name, version, nbextension=None):
    good_version = version.startswith(version_check_packages[package_name])
    if nbextension is None:
        nbextension = package_name
    if not good_version:
        print(
            "\n**** Please upgrade {} to version {} by running:".format(
                package_name, version_check_packages[package_name]
            )
        )
        print("        conda remove --force {} # if you use conda".format(package_name))
        print("        pip install --pre --upgrade {}".format(package_name))
        print("        jupyter nbextension enable --py {}".format(nbextension))
    else:
        print("{} version is good!".format(package_name))


# Check as many packages as we can...

try:
    import matplotlib
except ImportError:
    pass
else:
    version_checker("matplotlib", matplotlib.__version__)

try:
    import NeuNorm
except ImportError:
    pass
else:
    version_checker("NeuNorm", NeuNorm.__version__)

try:
    import PIL
except ImportError:
    pass
else:
    version_checker("Pillow", PIL.__version__)

try:
    import scipy
except ImportError:
    pass
else:
    version_checker("scipy", scipy.__version__)

try:
    import skimage
except ImportError:
    pass
else:
    version_checker("scikit-image", skimage.__version__)

try:
    import numpy
except ImportError:
    pass
else:
    version_checker("numpy", numpy.__version__)

try:
    import ipywidgets
except ImportError:
    pass
else:
    version_checker("ipywidgets", ipywidgets.__version__)

try:
    import pandas
except ImportError:
    pass
else:
    version_checker("pandas", pandas.__version__)

try:
    import plotly
except ImportError:
    pass
else:
    version_checker("plotly", plotly.__version__)

try:
    import pyqtgraph
except ImportError:
    pass
else:
    version_checker("pyqtgraph", pyqtgraph.__version__)

try:
    import sectorizedradialprofile  # noqa: F401
except ImportError:
    pass
else:
    version_checker("sectorizedradialprofile", "N/A")

try:
    import pyoncat
except ImportError:
    pass
else:
    version_checker("pyoncat", pyoncat.__version__)

try:
    import oauthlib
except ImportError:
    pass
else:
    version_checker("oauthlib", oauthlib.__version__)

try:
    import tifffile
except ImportError:
    pass
else:
    version_checker("tifffile", tifffile.__version__)

try:
    import qtpy
except ImportError:
    pass
else:
    version_checker("qtpy", qtpy.__version__)
