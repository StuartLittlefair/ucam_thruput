from __future__ import (print_function, absolute_import)
from setuptools import setup
import os
import glob

requirements = [
    'numpy',
    'astropy'
]

setup(
    name="ucam_thruput",
    version="0.1",
    description="Instrument Simulations for HiPERCAM, ULTRACAM, ULTRASPEC",
    author_email="s.littlefair@shef.ac.uk",
    packages=['ucam_thruput'],
    package_data={'': ['data/*']},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False
)
