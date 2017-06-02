#! /usr/bin/env python
# Fix filter bandpass files from Vik Dhillon's ULTRACAM page into a
# suitable format for pysynphot, and adjust for the f-ratio of the
# beam.
from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
import pysynphot as S


def get_comments(fname):
    comments = []
    with open(fname) as f:
        for line in f:
            if line.startswith('#'):
                comments.append(line)
    return comments


def read_filter_file(fname):
    try:
        x, y = np.loadtxt(in_fname).T
    except:
        # format 2
        # date
        # time
        # min wavelengt, max wavelength
        # ?, ?
        # ?, step
        f = open(fname)
        lines = f.readlines()
        start, end = (float(x) for x in lines[2].split(','))
        _, step = (float(x) for x in lines[4].split(','))
        y = np.array([float(val.strip()) for val in lines[5:]])
        x = end - step*np.arange(len(y))
        # check we're close to the end value
        assert np.allclose(x.min(), start)
    return x, y


def fix_filter(in_fname, out_fname, f_ratio):
    x, y = read_filter_file(in_fname)
    # x should be in AA, but is sometimes nm
    if x.min() < 1000:
        x *= 10
    # should be in ascending order of x
    indices = np.argsort(x)
    x, y = x[indices], y[indices]

    # f-ratio fix, assuming n=1.5
    # ULTRACAM is f/2.3, HiPERCAM is f/2.47
    theta = np.degrees(np.arctan(1/f_ratio/2))
    n = 1.5
    lambda_central = S.ArrayBandpass(x, y).pivot()
    shift = 0.5*lambda_central*(np.sqrt(n**2-np.sin(theta)**2)/n - 1)
    x -= shift

    # if y is >1 we are in %
    if y.max() > 1.5:
        y /= 100

    np.savetxt(out_fname, np.column_stack((x, y)))


if __name__ == "__main__":
    import sys
    inst, in_fname, out_fname = sys.argv[1:]
    assert inst in ('hcam', 'ucam')
    out_fname = inst + '_' + out_fname + ".txt"
    f_ratio = {'hcam': 2.47, 'ucam':2.3}[inst]

    fix_filter(in_fname, out_fname, f_ratio)
