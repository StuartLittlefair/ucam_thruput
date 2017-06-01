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

.. image:: https://raw.github.com/StuartLittlefair/ucam_thruput/master/images/ULTRASPEC.png
