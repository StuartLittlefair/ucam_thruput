ULTRACAM/HiperCAM/ULTRASPEC Throughput Models
===================================

``ucam_thruput`` provides throughput models for the instruments HiperCAM, ULTRACAM
and ULTRASPEC, and some tools for using these throughput models with the Python
module `pysynphot <http://pysynphot.readthedocs.io/en/latest/>`_.

Installation
------------

The software is written as much as possible to make use of core Python
components. The only third-party requirements are `astropy <http://astropy.org/>`_,
``numpy`` and, optionally, `graphviz <http://graphviz.readthedocs.io/en/stable/manual.html>`_
 for making pretty graphical illustrations of the lightpath through the instruments.

Once you have installed these, download the module and install with the usual::

 pip install .

or if you don't have root access::

 pip install --user .

For more information, see:

* `This packages' Github code repository <https://github.com/StuartLittlefair/ucam_thruput>`_

Usage
-----

..note::
    This module (and the instructions below) was written to be used with `pysynphot <http://pysynphot.readthedocs.io/en/latest/>`_.
    The synphot code is being re-factored into a general purpose package `synphot <http://synphot.readthedocs.io/en/latest/>`_
    and an extension that implements HST and JWST specific functionality - `stsynphot <http://stsynphot.readthedocs.io/en/latest/>`_.

    ``ucam_thruput`` can be used with the new modules if you prefer. See the `synphot instructions`_ for more info.

.. _synphot instructions: synphot_info.rst

First of all, follow the installation directions for `pysynphot <http://pysynphot.readthedocs.io/en/latest/>`_
(whilst the module will install without ``pysynphot``, it won't do much!). Make sure you
also install some of the data files, in particular those in the ``synphot1.tar.gz`` archive.
Set the ``PYSYN_CDBS`` environment variable to the location of these data files.

When you use the module for the first time, some data files must be installed.
You can do this from inside Python:

.. code-block:: python
    from ucam_thruput import setup
    setup()

You will only need to do this once. Once setup, you can then enable the
``ucam_thruput`` models in Python like so:

.. code-block:: python

    import pysynphot as S
    from ucam_thruput import getref

    # now make pysynphot use our throughput models
    # we specify a telescope here so that we set the primary area
    setup_dictionary = getref('tnt')
    S.setref(**setup_dictionary)

You can switch back to using the built-in ``pysynphot`` models (including HST instruments,
and Johnson/SDSS filters) at any time

.. code-block:: python

    S.setref(comptable=None, graphtable=None)  # leave the telescope area as it was
    S.setref(area=None)  # reset the telescope area as well

Once ``pysynphot`` is setup to use the ``ucam_thruput`` models, we can define a
`BandPass <http://pysynphot.readthedocs.io/en/latest/bandpass.html>`_ using a
string of specified instrument mode keywords:

.. code-block:: python

    # make a bandpass object using an obsmode string
    bp = S.ObsBandPass('uspec,tnt,g')

These bandpasses can be used with ``pysynphot`` in the usual way. See the
``pysynphot`` `docs <http://pysynphot.readthedocs.io/en/latest>`_ for full
information.

A complete observing mode string specfies the telescope (gtc, tnt, wht, ntt or vlt),
the instrument (ucam, uspec, hcam) and a filter. Additional keywords can be used that
allow one to ignore the atmosphere (noatmos), insert the scintillation corrector
(scint_corr), use the old NTT/ULTRACAM collimator (old) or use the NTT cube (cube).
Not all combinations of keywords are valid. A full list of keywords, including all filters,
can be found using the ``list_keywords`` function.

.. code-block:: python

    from ucam_thruput import list_keywords
    list_keywords()

Models
------

Below are graphical representations of the instrument throughput models. The light paths
are shown as a series of nodes, connected by edges (lines). Each edge represents the
application of a transparency curve. If a line is labelled by a keyword, that path will
only be taken if the keyword is present in the string used to define the
`BandPass <http://pysynphot.readthedocs.io/en/latest/bandpass.html>`_.

Dashed lines represent "clear" transparency curves, that do not affect the throughput.
Red lines represent reflections from dichroic surfaces. Unlabelled lines represent the default
path.

**Common** - entry path followed by all instruments

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/common.png

**ULTRACAM**

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/ucam.png

**HiperCAM**

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/hcam.png

**ULTRASPEC**

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/uspec.png


Examples
--------

A few example uses are shown below. These assume you've downloaded many of the PySynphot data files
and installed them in a directory referenced by the environment variable ```PYSYN_CDBS```.

The following example calculates the colour terms of USPEC/TNT g'-band.

.. code-block:: python

    import os
    from matplotlib import pyplot as plt
    import numpy as np
    from ucam_thruput import setup, getref
    import pysynphot as S

    pickles_path = os.path.join(os.environ['PYSYN_CDBS'], 'grid', 'pickles', 'dat_uvk')
    pickles_ms = (
        ('pickles_uk_1',    'O5V',     39810.7),
        ('pickles_uk_2',    'O9V',     35481.4),
        ('pickles_uk_3',    'B0V',     28183.8),
        ('pickles_uk_4',    'B1V',     22387.2),
        ('pickles_uk_5',    'B3V',     19054.6),
        ('pickles_uk_6',    'B5-7V',   14125.4),
        ('pickles_uk_7',    'B8V',     11749.0),
        ('pickles_uk_9',    'A0V',     9549.93),
        ('pickles_uk_10',   'A2V',     8912.51),
        ('pickles_uk_11',   'A3V',     8790.23),
        ('pickles_uk_12',   'A5V',     8491.80),
        ('pickles_uk_14',   'F0V',     7211.08),
        ('pickles_uk_15',   'F2V',     6776.42),
        ('pickles_uk_16',   'F5V',     6531.31),
        ('pickles_uk_20',   'F8V',     6039.48),
        ('pickles_uk_23',   'G0V',     5807.64),
        ('pickles_uk_26',   'G2V',     5636.38),
        ('pickles_uk_27',   'G5V',     5584.70),
        ('pickles_uk_30',   'G8V',     5333.35),
        ('pickles_uk_31',   'K0V',     5188.00),
        ('pickles_uk_33',   'K2V',     4886.52),
        ('pickles_uk_36',   'K5V',     4187.94),
        ('pickles_uk_37',   'K7V',     3999.45),
        ('pickles_uk_38',   'M0V',     3801.89),
        ('pickles_uk_40',   'M2V',     3548.13),
        ('pickles_uk_43',   'M4V',     3111.72),
        ('pickles_uk_44',   'M5V',     2951.21)
    )

    uspec_g = []
    sdss_g = []
    sdss_r = []
    S.setref(**getref('tnt'))
    for name, spt, teff in pickles_ms:
        sp = S.FileSpectrum(os.path.join(pickles_path, name+'.fits'))

        bp = S.ObsBandpass('uspec,tnt,g')
        obs = S.Observation(sp, bp, force='taper')
        uspec_g.append(obs.effstim('abmag'))

    S.setref(comptable=None, graphtable=None)
    for name, spt, teff in pickles_ms:
        sp = S.FileSpectrum(os.path.join(pickles_path, name+'.fits'))
        bp = S.ObsBandpass('sdss,r')
        obs = S.Observation(sp, bp, force='taper')
        sdss_r.append(obs.effstim('abmag'))
        bp = S.ObsBandpass('sdss,g')
        obs = S.Observation(sp, bp, force='taper')
        sdss_g.append(obs.effstim('abmag'))

    uspec_g = np.array(uspec_g)
    sdss_g = np.array(sdss_g)
    sdss_r = np.array(sdss_r)
    plt.plot(sdss_g - sdss_r, uspec_g - sdss_g, 'r.')
    plt.xlabel("g'-r'")
    plt.ylabel("uspec_g - g'")
    plt.show()

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/uspec_g_colour_terms.png

------------

Here is an example that plots the various contributions to a bandpass.

.. code-block:: python

    import os

    import pysynphot as S
    from ucam_thruput import getref
    from matplotlib import pyplot as plt

    S.setref(**getref('tnt'))
    bp = S.ObsBandpass('uspec,tnt,g')

    plt.plot(bp.wave, bp.throughput, 'k-')
    for comp in bp.complist():
        name = os.path.splitext(os.path.split(comp.name)[1])[0]
        if name != 'alum':
            plt.plot(comp.wave, comp.throughput, ls='--', label=name)

    plt.legend()
    plt.show()

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/uspec_g_thruput.png
