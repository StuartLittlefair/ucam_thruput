# glass transmission data from refractiveindex.info for Schott glasses

import sys
import os
import numpy as np
from scipy.interpolate import interp1d

page_ids = {
    'N-PSK3': 965,
    'CaF2': 851,
    'LLF1': 977,
    'N-SK16': 924,
    'N-LAK10': 953,
    'SF2': 980,
    'N-SF1': 995,
    'N-LAK22': 957,
    'silica': 835
}

refr_db_path = '/Users/sl/code/python/github-packages/refractiveindex.info-sqlite'
sys.path.append(refr_db_path)
from refractivesqlite import dboperations as DB

dbpath = os.path.join(refr_db_path, 'refractive.db')
db = DB.Database(dbpath)


def get_transmittance(glass, thickness):
    # thickness in mm
    glass_id = page_ids[glass]
    query = f'select wave,coeff from extcoeff where pageid={glass_id} and wave between 0.2 and 2.5'
    r = db.search_custom(query)
    wav, k = list(zip(*r))
    alpha = 4*np.pi*np.array(k)/np.array(wav)
    tau = np.exp(-1 * thickness * 1e3 * alpha)
    x = np.array(wav) * 10000
    f = interp1d(x, tau, kind='linear',
                 bounds_error=False, fill_value=0.0)
    return f
