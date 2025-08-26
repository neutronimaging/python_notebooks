"""
Test that all required packages can be imported successfully.

This ensures that the environment is correctly set up with all dependencies.
"""

import importlib

import pytest

# List of all packages that should be importable
REQUIRED_PACKAGES = [
    "astropy",
    "scipy",
    "pandas",
    "skimage",
    "h5py",
    "lmfit",
    "matplotlib",
    "plotly",
    "dash",
    "jupyterlab",
    "ipympl",
    "ipywidgets",
    "jupytext",
    "nbstripout",
    "xlrd",
    "openpyxl",
    "xlsxwriter",
    "PyQt5",
    "pyqtgraph",
    "tqdm",
    "pyoncat",
    "pytest",
    "NeuNorm",  # imports as NeuNorm, not neunorm
    "neutronbraggedge",
    "ImagingReso",
    "changepy",
    "sectorizedradialprofile",
    "ipywe",
]


@pytest.mark.parametrize("package_name", REQUIRED_PACKAGES)
def test_package_import(package_name):
    """Test that each required package can be imported."""
    try:
        importlib.import_module(package_name)
    except ImportError as e:
        pytest.fail(f"Failed to import {package_name}: {e}")


def test_critical_notebook_utilities():
    """Test that critical notebook utilities are importable."""
    # Add any critical local modules from notebooks/__code/ here
    # Example:
    # from __code import file_handler
    # from __code import metadata_handler
    pass  # Remove this when adding actual imports
