#!/usr/bin/env python
from setuptools import setup, find_packages, Command
import os
import codecs
import sys
from shutil import rmtree

import version

# to create library
# > python setup.py upload

NAME = 'Neutron Imaging Notebooks'
DESCRIPTION = "Set of jupyter notebooks for neutron imaging work"
LONGDESCRIPTION = "See the full tutorial of the notebooks on https://neutronimaging.pages.ornl.gov/tutorial/notebooks/"
URL = "https://neutronimaging.pages.ornl.gov/tutorial/notebooks/"
EMAIL = "bilheuxjm@ornl.gov"
AUTHOR = "Jean Bilheux"
VERSION = version.__version__
KEYWORDS = "neutron analysis imaging"

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


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
            rmtree(os.path.join(THIS_DIR, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution...')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


def read_requirements_from_file(filepath):
    '''Read a list of requirements from the given file and split into a
    list of strings. It is assumed that the file is a flat
    list with one requirement per line.
    :param filepath: Path to the file to read
    :return: A list of strings containing the requirements
    '''
    with open(filepath, 'r') as req_file:
        return req_file.readlines()


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(THIS_DIR, *parts), "rb", "utf-8") as f:
        return f.read()


install_requires = read_requirements_from_file(os.path.join(THIS_DIR, 'requirements.txt'))
REQUIRED = ['numpy',
            'pillow',
            'jupyter']
setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=LONGDESCRIPTION,
    url=URL,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(exclude=['tests', 'notebooks']),
    package_data={'': ["*.ui"]},
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
