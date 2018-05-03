from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from itertools import chain
import os
import datetime

import numpy as np
from astropy.table import Table

INSTRUMENT_TABLE_NAME = 'ucam_thruput_tmg.fits'
COMPONENT_TABLE_NAME = 'ucam_thruput_tmc.fits'


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
    if not os.path.exists(itable) or not os.path.exists(mtable):
        _install_table_files()
    return itable, mtable


def list_keywords():
    """
    Get all the keywords that can be used to define obsmodes.
    """
    itable, _ = _check_tables()
    itable = Table.read(itable)
    kws = set(itable['KEYWORD'])
    kws.remove('default')
    return kws


def _install_table_files():
    itable = _make_instrument_reference_table()
    mtable = _make_component_table(itable)
    user_dir = _check_user_dir()
    itable.write(os.path.join(user_dir, INSTRUMENT_TABLE_NAME),
                 overwrite=True)
    mtable.write(os.path.join(user_dir, COMPONENT_TABLE_NAME),
                 overwrite=True)


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
    filenames = [component + '.txt' for component in components]
    now = datetime.datetime.now()
    time_string = now.strftime('%b %d %Y %H:%M:%S').lower()
    for component, filename in zip(components, filenames):
        table.add_row((time_string, component, filename, 'ultracam group throughput'))
    return table
