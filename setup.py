from __future__ import absolute_import, print_function

import glob
import os

from setuptools import setup

requirements = ["numpy", "astropy", "synphot", "stsynphot"]

setup(
    name="ucam_thruput",
    version="0.1",
    description="Instrument Simulations for HiPERCAM, ULTRACAM, ULTRASPEC",
    author_email="s.littlefair@shef.ac.uk",
    packages=["ucam_thruput"],
    package_data={"": ["data/*"]},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
)
