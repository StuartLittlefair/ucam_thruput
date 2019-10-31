from dataclasses import dataclass
from typing import List
import numpy as np
import glob
import os
import pandas as pd
from scipy.interpolate import interp1d
from glass_transmission import get_transmittance


def transmission_at_surface(material, wavs):
    sheet_path = '/Users/sl/code/python/github-packages/ucam_thruput/data/ucam_ar_coatings'
    sheets = glob.glob(os.path.join(sheet_path, '*.xls'))
    for sheet in sheets:
        if material in sheet:
            break
    df = pd.read_excel(sheet, skiprows=1, names=['Wav', 'R', 'T'])
    x = df['Wav'] * 10
    y = df['T']
    f = interp1d(x, y, kind='cubic',
                 bounds_error=False, fill_value=0.0)
    return f(wavs)


@dataclass
class Element:
    material: str = 'Air'
    thickness: float = 0.0


@dataclass
class Camera:
    elements: List[Element]
    wavs: List[float] = np.linspace(2000, 11000, 300)

    @property
    def n_elements(self):
        return len(self.elements)

    @property
    def throughput(self):
        result = np.ones_like(self.wavs)
        for i in range(self.n_elements - 1):
            this_material = self.elements[i].material
            next_material = self.elements[i+1].material
            # reflections at boundaries
            if this_material != 'Air' and next_material != 'Air':
                # glass-to-glass, no reflection (could be better - need glue specs)
                result *= 1
            else:
                # glass-to-air, or air-to-glass, use AR coating data
                material = this_material if next_material == 'Air' else next_material
                result *= transmission_at_surface(material, self.wavs)
            # transmission within element
            if this_material != 'Air':
                transmittance = get_transmittance(this_material, self.elements[i].thickness)
                result *= transmittance(self.wavs)
        return result

    @property
    def bulk_transmission(self):
        result = np.ones_like(self.wavs)
        for i in range(self.n_elements - 1):
            this_material = self.elements[i].material
            # transmission within element
            if this_material != 'Air':
                transmittance = get_transmittance(this_material, self.elements[i].thickness)
                result *= transmittance(self.wavs)
        return result

    @property
    def reflections(self):
        result = np.ones_like(self.wavs)
        for i in range(self.n_elements - 1):
            this_material = self.elements[i].material
            next_material = self.elements[i+1].material
            # reflections at boundaries
            if this_material != 'Air' and next_material != 'Air':
                # glass-to-glass, no reflection (could be better - need glue specs)
                result *= 1
            else:
                # glass-to-air, or air-to-glass, use AR coating data
                material = this_material if next_material == 'Air' else next_material
                result *= transmission_at_surface(material, self.wavs)
        return result


collimator = Camera(
    [
        Element(),
        Element('N-PSK3', 12.043),
        Element(),
        Element('CaF2', 16.95),
        Element(),
        Element('LLF1', 7),
        Element(),
        Element('CaF2', 17.7),
        Element()
    ]
)

uband = Camera(
    [
        Element(),
        Element('N-SK16', 6.054),
        Element(),
        Element('N-SK16', 7.937),
        Element('LLF1', 2.425),
        Element(),
        Element('LLF1', 2.513),
        Element('N-SK16', 7.881),
        Element(),
        Element('N-SK16', 6.033),
        Element()
    ]
)

gband = Camera(
    [
        Element(),
        Element('N-LAK10', 6.357),
        Element(),
        Element('N-LAK10', 7.934),
        Element('SF2', 2.445),
        Element(),
        Element('SF2', 2.585),
        Element('N-LAK10', 7.51),
        Element(),
        Element('N-LAK10', 6.075),
        Element()
    ]
)

rband = Camera(
    [
        Element(),
        Element('N-LAK22', 6.031),
        Element(),
        Element('N-LAK22', 8.003),
        Element('N-SF1', 2.396),
        Element(),
        Element('N-SF1', 2.5),
        Element('N-LAK22', 6.805),
        Element(),
        Element('N-LAK22', 5.408),
        Element()
    ]
)

if __name__ == "__main__":
    np.savetxt('../ucam_thruput/data/ucam_cam_bl.txt', np.column_stack((uband.wavs, uband.throughput)))
    np.savetxt('../ucam_thruput/data/ucam_cam_grn.txt', np.column_stack((gband.wavs, gband.throughput)))
    np.savetxt('../ucam_thruput/data/ucam_cam_red.txt', np.column_stack((rband.wavs, rband.throughput)))
    np.savetxt('../ucam_thruput/data/ucam_coll_wht.txt',
               np.column_stack((collimator.wavs, collimator.throughput)))
    np.savetxt('../ucam_thruput/data/ucam_coll_ntt.txt',
               np.column_stack((collimator.wavs, collimator.throughput)))
    np.savetxt('../ucam_thruput/data/ucam_coll_ntt_old.txt',
               np.column_stack((collimator.wavs, collimator.throughput)))
