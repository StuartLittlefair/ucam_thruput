from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from itertools import chain
import os
import datetime
import pkg_resources
import glob
import shutil

import numpy as np
from astropy.table import Table

INSTRUMENT_TABLE_NAME = 'ucam_thruput_tmg.fits'
COMPONENT_TABLE_NAME = 'ucam_thruput_tmc.fits'
# telescope areas in cm**2, corrected for obstructions
TELESCOPE_AREAS = dict(
    ntt=90091.45,  # 3.58m, 1.16m obstruction
    vlt=518319.9,  # 8.2m, 1.116m obstruction with no baffle
    wht=127234.5,  # 4.2m, 1.2m obstruction
    gtc=730000.0,  # ?
    tnt=37384.9,   # 2.3m clear aperture (2.4m, 1m obstruction)
)


def _check_user_dir():
    """
    Check directories exist for saving apps/configs etc. Create if not.
    """
    direc = os.path.expanduser('~/.ucam_thruput')
    if not os.path.exists(direc):
        os.mkdir(direc)
    return direc


def _check_tables():
    user_dir = _check_user_dir()
    itable = os.path.join(user_dir, INSTRUMENT_TABLE_NAME)
    mtable = os.path.join(user_dir, COMPONENT_TABLE_NAME)
    if not os.path.exists(itable):
        raise ValueError('Instrument graphtable {} is not installed'.format(INSTRUMENT_TABLE_NAME))
    if not os.path.exists(mtable):
        raise ValueError('Component table {} is not installed'.format(COMPONENT_TABLE_NAME))
    return itable, mtable


def getref(telescope):
    """
    Get dictionary used to setup pysynphot to use ULTRACAM tables

    Parameters
    ----------
    telescope : string
        Telescope observations will be made at. Used to set primary area.
    """
    assert telescope in TELESCOPE_AREAS
    itable, mtable = _check_tables()
    ref_dict = dict(
        area=TELESCOPE_AREAS[telescope],
        graphtable=itable,
        comptable=mtable
    )
    return ref_dict


def setup():
    """
    Install all necessary files into the user's home directory and PySynphot installation.
    """
    _install_table_files()
    _install_throughput_files()


def _install_table_files():
    itable = _make_instrument_reference_table()
    mtable = _make_component_table(itable)
    user_dir = _check_user_dir()
    itable.write(os.path.join(user_dir, INSTRUMENT_TABLE_NAME),
                 overwrite=True)
    mtable.write(os.path.join(user_dir, COMPONENT_TABLE_NAME),
                 overwrite=True)


def _install_throughput_files():
    pysyn_cdbs = os.getenv('PYSYN_CDBS')
    if pysyn_cdbs is None:
        err_msg = """
            PYSYN_CDBS environment variable is not set.
            Perhaps pysynphot is not installed, or you haven't correctly set up
            pysynphot according to the instructions at

            http://pysynphot.readthedocs.io/en/latest/index.html

            In particular, be sure to install synphot1.tar.gz.
            """
        raise ValueError(err_msg)

    pysyn_cdbs = os.path.join(pysyn_cdbs, 'comp/nonhst')
    if not os.path.exists(pysyn_cdbs):
        err_msg = """
            Directory $PYSYN_CDBS/comp/nonhst does not exist.
            Perhaps pysynphot is not installed, or you haven't correctly set up
            pysynphot according to the instructions at

            http://pysynphot.readthedocs.io/en/latest/index.html

            In particular, be sure to install synphot1.tar.gz.
            """
        raise ValueError(err_msg)

    resource_dir = pkg_resources.resource_filename('ucam_thruput', 'data')
    for filename in glob.glob(os.path.join(resource_dir, '*.txt')):
        shutil.copy(filename, pysyn_cdbs)


def _make_instrument_reference_table():
    from .ucam import Ucam
    from .uspec import Uspec
    from .common import Common
    from .hcam import Hcam
    c = Common()
    u = Ucam()
    us = Uspec()
    hc = Hcam()
    rows = list(chain(*(c.instrument_table_rows,
                        u.instrument_table_rows,
                        hc.instrument_table_rows,
                        us.instrument_table_rows)))
    rows = sorted(rows, key=lambda x: x[2])

    table = Table(names=['COMPNAME', 'KEYWORD', 'INNODE', 'OUTNODE', 'THCOMPNAME', 'COMMENT'],
                  dtype=(np.dtype((str, 18)), np.dtype((str, 20)), 'int32', 'int32',
                         np.dtype((str, 20)), np.dtype((str, 68))))
    for row in rows:
        table.add_row(row)
    return table


def _make_component_table(itable):
    table = Table(names=['TIME', 'COMPNAME', 'FILENAME', 'COMMENT'],
                  dtype=(np.dtype((str, 26)), np.dtype((str, 18)),
                         np.dtype((str, 50)), np.dtype((str, 68))))
    components = set(itable['COMPNAME'])
    filenames = ['crnonhstcomp$' + component + '.txt' for component in components]
    now = datetime.datetime.now()
    time_string = now.strftime('%b %d %Y %H:%M:%S').lower()
    for component, filename in zip(components, filenames):
        table.add_row((time_string, component, filename, 'ultracam group throughput'))
    return table
