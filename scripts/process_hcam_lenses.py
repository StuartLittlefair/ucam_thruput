import pandas as pd
import numpy as np
from string import ascii_letters
from scipy.interpolate import interp1d
import os


def col2num(col):
    # excel column name to number
    num = 0
    for c in col:
        if c in ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num - 1


def calc_barrel(df, barrel):
    xgrid = np.linspace(0.2, 1.1, 300)
    ygrid = np.ones_like(xgrid)
    for lens in barrel['lenses']:
        for element in lens:
            xcol = col2num(element[0])
            ycol = col2num(element[1])

            xdata = df.iloc[:, xcol].dropna()
            ydata = df.iloc[:, ycol].dropna()

            f = interp1d(xdata, ydata, kind='linear',
                         bounds_error=False, fill_value='extrapolate')
            y = f(xgrid)
            y[y < 0] = 0
            ygrid *= y
    f = interp1d(xgrid, ygrid, kind='cubic')
    ygrid = f(xgrid)
    ygrid[ygrid < 0] = 0
    return xgrid, ygrid


sheet_path = '/Users/sl/code/python/github-packages/ucam_thruput/data/'
save_path = '/Users/sl/code/python/github-packages/ucam_thruput/ucam_thruput/data'


def process_barrel(barrel, ofname):
    sheet = os.path.join(sheet_path, barrel['sheet'])
    df = pd.read_excel(sheet)
    x, y = calc_barrel(df, barrel)
    # convert x from microns to angstrom
    x *= 10000
    np.savetxt(os.path.join(save_path, ofname),
               np.column_stack((x, y)))


collimator = dict(
    sheet='collimator.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab')),
        (('ad', 'af'), ('ah', 'aj'), ('al', 'an')),
        (('ap', 'ar'), ('at', 'av'), ('ax', 'az'))
    ]
)

uband = dict(
    sheet='ucam.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab'), ('ad', 'af'), ('ah', 'aj')),
        (('al', 'an'), ('ap', 'ar'), ('at', 'av'), ('ax', 'az'), ('bb', 'bd')),
        (('bf', 'bh'), ('bj', 'bl'), ('bn', 'bp'))
    ]
)

gband = dict(
    sheet='gcam.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab'), ('ad', 'af'), ('ah', 'aj')),
        (('al', 'an'), ('ap', 'ar'), ('at', 'av'), ('ax', 'az'), ('bb', 'bd')),
        (('bf', 'bh'), ('bj', 'bl'), ('bn', 'bp'))
    ]
)

rband = dict(
    sheet='rcam.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab'), ('ad', 'af'), ('ah', 'aj')),
        (('al', 'an'), ('ap', 'ar'), ('at', 'av'), ('ax', 'az'), ('bb', 'bd')),
        (('bf', 'bh'), ('bj', 'bl'), ('bn', 'bp'))
    ]
)

iband = dict(
    sheet='icam.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab'), ('ad', 'af'), ('ah', 'aj')),
        (('al', 'an'), ('ap', 'ar'), ('at', 'av'), ('ax', 'az'), ('bb', 'bd')),
        (('bf', 'bh'), ('bj', 'bl'), ('bn', 'bp'))
    ]
)

zband = dict(
    sheet='zcam.xlsx',
    lenses=[
        (('f', 'h'), ('j', 'l'), ('n', 'p')),
        (('r', 't'), ('v', 'x'), ('z', 'ab'), ('ad', 'af'), ('ah', 'aj')),
        (('al', 'an'), ('ap', 'ar'), ('at', 'av'), ('ax', 'az'), ('bb', 'bd')),
        (('bf', 'bh'), ('bj', 'bl'), ('bn', 'bp'))
    ]
)

process_barrel(collimator, 'hcam_coll_gtc.txt')
process_barrel(collimator, 'hcam_coll_wht.txt')
process_barrel(uband, 'hcam_cam_u.txt')
process_barrel(gband, 'hcam_cam_g.txt')
process_barrel(rband, 'hcam_cam_r.txt')
process_barrel(iband, 'hcam_cam_i.txt')
process_barrel(zband, 'hcam_cam_z.txt')