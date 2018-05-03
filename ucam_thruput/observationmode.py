"""
Module for handling observations based on observation modes.

Largely copied and pasted from stsynphot (https://github.com/spacetelescope/stsynphot_refactor)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import warnings

from astropy import units as u
from astropy import log
from astropy.utils.decorators import lazyproperty
from astropy.utils.exceptions import AstropyUserWarning

# SYNPHOT
from synphot import units as syn_units
from synphot.models import Empirical1D
from synphot.spectrum import SpectralElement

from .tables import GraphTable, CompTable
from . import _check_tables

# telescope areas in cm**2, corrected for obstructions
TELESCOPE_AREAS = dict(
    ntt=90091.45*u.cm*u.cm,  # 3.58m, 1.16m obstruction
    vlt=518319.9*u.cm*u.cm,  # 8.2m, 1.116m obstruction with no baffle
    wht=127234.5*u.cm*u.cm,  # 4.2m, 1.2m obstruction
    gtc=730000.0*u.cm*u.cm,  # ?
    tnt=37384.9*u.cm*u.cm,   # 2.3m clear aperture (2.4m, 1m obstruction)
)


class Component(object):
    """Class to handle individual components in `BaseObservationMode`.

    Parameters
    ----------
    throughput_name : str
        Component filename.

    Attributes
    ----------
    throughput_name : str
        Component filename.

    throughput : `synphot.spectrum.SpectralElement` or `None`
        Component spectrum object.
    """
    def __init__(self, throughput_name):
        self.throughput_name = throughput_name

        # Extract bandpass unless component is a CLEAR filter.
        if throughput_name != 'clear':
            self.throughput = SpectralElement.from_file(throughput_name)
        else:
            self.throughput = None

    @property
    def empty(self):
        """`True` if ``self.throughput`` is empty."""
        return self.throughput is None

    def __str__(self):
        return str(self.throughput)


class BaseObservationMode(object):
    """Base class to handle an observation.

    Uses the graph and optical component tables.

    .. note::
        ``pixscale`` is set from ``stsynphot.config.conf.detectorfile``,
        which is parsed with :func:`stsynphot.stio.read_detector_pars`.
        ``binset`` is set by ``stsynphot.wavetable.WAVECAT``.

    Parameters
    ----------
    obsmode : str
        Observation mode.

    Attributes
    ----------
    modes : list
        List of individual modes within observation mode.

    gtname, ctname : str
        Graph and component table filenames.
    compnames : list of str
        Optical components.
    components : list of obj
        List of component objects.
    primary_area : `astropy.units.quantity.Quantity`
        Telescope collecting area.
    pixscale : `astropy.units.quantity.Quantity`
        Detector pixel scale.
    binset : str
        Wavelength table filename/param string from matching obsmode.
    bandwave : `astropy.units.quantity.Quantity`
        Wavelength set defined by ``binset``.
    """
    def __init__(self, obsmode):
        self.gtname, self.ctname = _check_tables()

        # Force lowercase
        self._obsmode = obsmode.lower()

        # Split obsmode and separate parameterized modes
        modes = self._obsmode.replace(' ', '').split(',')
        self.modes = modes

        # Get graph table and primary area
        gt = GraphTable(self.gtname)
        telescope = set([mode for mode in modes if (mode in TELESCOPE_AREAS)])
        if len(telescope) > 1:
            raise ValueError('ambiguous telescope in ObsMode: found {}'.format(telescope))

        self.primary_area = TELESCOPE_AREAS[telescope.pop()]

        # Get optical and thermal components
        self.compnames, self.thcompnames = gt.get_comp_from_gt(self.modes, 1)

        # Use default optical component table
        ct = CompTable(self.ctname)

        # Set by sub-classes
        self.components = None

        # Get optical component filenames
        self._throughput_filenames = ct.get_filenames(self.compnames)

        # Set detector pixel scale
        # self._set_pixscale()

        # For sensitivity calculations
        self._constant = self.primary_area / syn_units.HC

        # Get wavelength set
        self.binset = ''
        self.bandwave = None

    def _set_pixscale(self):
        """Set pixel scale.
        """
        self.pixscale = 0.33 * u.arcsec

    def _get_components(self):
        raise NotImplementedError('To be implemented by subclasses.')

    def __str__(self):
        return self._obsmode

    def __len__(self):
        return len(self.components)

    def showfiles(self):  # pragma: no cover
        """Display optical component filenames."""
        info_str = '#Throughput table names:\n'
        for name in self._throughput_filenames:
            if name != 'clear':
                info_str += '{0}\n'.format(name)
        log.info(info_str.rstrip())


class ObservationMode(BaseObservationMode):
    """
    Class to handle an observation mode.

    See `BaseObservationMode` for additional attributes.

    Parameters
    ----------
    obsmode
        See `BaseObservationMode`.
    """
    def __init__(self, obsmode):
        super(ObservationMode, self).__init__(obsmode)
        self._component_dict = dict()
        self.components = self._get_components()

    def _get_components(self):
        """
        Get optical components
        """
        components = []
        for throughput_name in self._throughput_filenames:
            if throughput_name not in self._component_dict:
                self._component_dict[throughput_name] = Component((throughput_name))

            component = self._component_dict[throughput_name]
            if not component.empty:
                components.append(component)

        return components

    def _mul_thru(self, index):
        """Multiply all component spectra starting at given index."""
        product = self.components[index].throughput

        if len(self.components) > index:
            for component in self.components[index + 1:]:
                if not component.empty:
                    product = product * component.throughput

        product.meta['header'] = ''  # Clean up messy header
        return product

    @lazyproperty
    def throughput(self):
        """Combined throughput from multiplying all the components together."""
        try:
            thru = self._mul_thru(0)
        except IndexError as e:  # pragma: no cover
            thru = None
            warnings.warn(
                'Graph table is broken: {0}'.format(str(e)),
                AstropyUserWarning)
        return thru

    @lazyproperty
    def sensitivity(self):
        """Sensitivity spectrum to convert flux in
        :math:`erg \\; cm^{-2} \\; s^{-1} \\; \\AA^{-1}` to
        :math:`count s^{-1} \\AA^{-1}`. Calculation is done by
        combining the throughput curves with
        :math:`\\frac{h \\; c}{\\lambda}` .
        """
        x = self.throughput.waveset
        y = self.throughput(x)
        thru = y.value * x.value * self._constant.value
        meta = {'expr': 'Sensitivity for {0}'.format(self._obsmode)}
        return SpectralElement(
            Empirical1D, points=x, lookup_table=thru, meta=meta)
