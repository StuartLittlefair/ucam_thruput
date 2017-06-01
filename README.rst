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
 - for making pretty graphical illustrations of the lightpath through the instruments.

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

You can then enable the ``ucam_thruput`` models in Python like so:

.. code-block:: python

    import pysynphot as S
    from ucam_thruput import getref

    # now make pysynphot use our throughput models
    # we specify a telescope here so that we set the primary area
    setup_dictionary = getref('tnt')

Once ``pysynphot`` is setup to use the ``ucam_thruput`` models, we can define a
`BandPass <http://pysynphot.readthedocs.io/en/latest/bandpass.html>`_ using a
string of specified instrument mode keywords:

.. code-block:: python

    # make a bandpass object using an obsmode string
    bp = S.ObsBandPass('uspec,tnt,g')

These bandpasses can be used with ``pysynphot`` in the usual way. See the
``pysynphot`` `docs <http://pysynphot.readthedocs.io/en/latest>`_ for full
information.

