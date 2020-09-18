#!/usr/bin/env python
from setuptools import setup, find_packages, Command
import os
import sys
from shutil import rmtree

import __code

# to create library
# > python setup.py upload

NAME = 'Neutron Imaging Notebooks'
DESCRIPTION = "Set of jupyter notebooks for neutron imaging work"
LONGDESCRIPTION = "See the full tutorial of the notebooks on https://neutronimaging.pages.ornl.gov/tutorial/notebooks/"
URL = "https://neutronimaging.pages.ornl.gov/tutorial/notebooks/"
EMAIL = "bilheuxjm@ornl.gov"
AUTHOR = "Jean Bilheux"
VERSION = __code.__version__
KEYWORDS = "neutron analysis imaging"

# what packages are required for this module to be executed
REQUIRED = ['numpy',
            'pillow',
            'pathlib',
            'astropy',
            'scipy',
            ]

here = os.path.abspath('./')

class UploadCommand(Command):
    """Support setup.py upload."""
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        """Initialization options."""
        pass

    def finalize_options(self):
        """Finalize options."""
        pass

    def run(self):
        """Remove previous builds."""
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution...')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    description=DESCRIPTION ,
    long_description=LONGDESCRIPTION,
    url=URL,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(exclude=['tests', 'notebooks']),
    include_package_data=True,
    test_suite='tests',
    install_requires=REQUIRED,
    dependency_links=[
    ],
    license='BSD',
    keywords=KEYWORDS,
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Scientific/Engineering :: Physics',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6'],
    cmdclass={
        'upload': UploadCommand,
    },
)

# End of file
