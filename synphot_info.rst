Using `ucam_thruput` with `synphot <http://synphot.readthedocs.io/en/latest/>`
===================================

If you are using the newer `synphot <http://synphot.readthedocs.io/en/latest/>`_ and
`stsynphot <http://stsynphot.readthedocs.io/en/latest/>`_ modules, you can still use `ucam_thruput`.
Installation is the same; first install those modules, and make sure the ``PYSYN_CDBS`` environment variable
points to the location of the `stsynphot` data files.

Using the `ucam_thruput` models is just a matter of changing the tables used by `stsynphot`
to create a bandpass from keywords.

.. code-block:: python

    import stsynphot as stsyn
    import os

    root = os.path.expanduser('~')
    graphtable = os.path.join(root, '.ucam_thruput/ucam_thruput_tmg.fits')
    comptable = os.path.join(root, '.ucam_thruput/ucam_thruput_tmc.fits')

    stsyn.conf.graphtable = graphtable
    stsyn.conf.comptable = comptable

The usage of `synphot <http://synphot.readthedocs.io/en/latest/>`_ is different to that required for
`pysynphot <http://pysynphot.readthedocs.io/en/latest/>`_. As an example, the code below recreates the plot
of a single bandpass and it's components from the README

.. code-block:: python

    import stsynphot as stsyn
    import os

    root = os.path.expanduser('~')
    graphtable = os.path.join(root, '.ucam_thruput/ucam_thruput_tmg.fits')
    comptable = os.path.join(root, '.ucam_thruput/ucam_thruput_tmc.fits')

    stsyn.conf.graphtable = graphtable
    stsyn.conf.comptable = comptable

    bp = stsyn.band('hcam,gtc,g_s')
    fig, ax = plt.subplots()
    ax.plot(bp.waveset, bp(bp.waveset))
    for comp in bp.obsmode.components:
        name = os.path.splitext(os.path.split(comp.throughput_name)[1])[0]
        if 'alum' in comp.throughput_name:
            continue
        thru = comp.throughput
        ax.plot(thru.waveset, thru(thru.waveset), ls='--', label=name)
    plt.legend()
