.. _module-simu:

1. Simulate training data
=========================

``dasdc simu`` uses discoal to generate simulated training sequences from
population-specific configuration files. Its output feeds
:doc:`calc_domain`.

Example
-------

Simulate every configuration in a directory:

.. code-block:: shell

   dasdc simu -i example/simu_config/ -o simu_data

Or run a single configuration:

.. code-block:: shell

   dasdc simu -i example/simu_config/chSel_configure.txt -o simu_data

Name each configuration ``<name>_configure.txt``. Its simulated output is
named ``<name>_simulation``. For multiple explicit input files, separate their
paths with commas. An input directory should contain only configuration files.

Command options
---------------
.. list-table::
   :header-rows: 1
   :widths: 31 14 55

   * - Option
     - Required
     - Description
   * - ``-i``, ``--config-file``
     - Yes
     - Configuration file, directory, or comma-separated files. The alias ``--config_file`` is also accepted.
   * - ``-o``, ``--out``
     - Yes
     - Output path for the simulated data.


.. _simulation-configuration:

Simulation configuration
------------------------

The five files in ``example/simu_config/`` represent hard selective sweep, hard linkage,
soft selective sweep, soft linkage and neutral examples. Parameters and values are
separated by spaces or tabs. Put each demographic ``en`` event on its own line.

The settings below describe the supplied examples; population-specific
parameters must be inferred for your study.

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - Parameter
     - Meaning
     - Example / guidance
   * - ``rep``
     - Number of simulated replicates
     - ``2500`` produces 2,500 simulated examples.
   * - ``hap``
     - Haploid sample size
     - ``100`` corresponds to 50 diploid individuals.
   * - ``len``
     - Simulated fragment length
     - ``100000`` bp (100 kb). The supplied discoal build is documented for fragments up to 220 kb; recompile for longer fragments.
   * - ``Pt``
     - Scaled mutation-parameter range (theta)
     - Provide population-specific lower and upper values.
   * - ``Pr``
     - Scaled recombination-parameter range (rho)
     - Provide population-specific lower and upper values.
   * - ``Pu``
     - Selection end time and sampling time
     - Example: ``0.0005982817348574893 0``.
   * - ``Pa``
     - Scaled selection-strength range (alpha)
     - Provide population-specific lower and upper values.
   * - ``Px``
     - Interval containing the selected site
     - ``0.475 0.525`` places the site in the central 5% of the fragment.
   * - ``Pxx``
     - Discontinuous intervals for the selected site
     - Example intervals: 0–0.475 and 0.525–1, outside the central interval.
   * - ``en``
     - Demographic size-change event
     - ``en t_scaled 0 size_ratio``: time in units of ``4 × N0`` generations and population size relative to the diploid reference size ``N0``. Repeat for multiple events; see :ref:`simulation-parameter-scaling`.


.. important::

   Prepare mutation rate, recombination rate, selection strength and
   demographic parameters for the population under study. The example values are not a
   substitute for population-specific estimates. See
   :doc:`../parameter_inference`.

About discoal
-------------

The repository includes a compiled discoal binary. If recompilation is needed,
use the `discoal source repository <https://github.com/kr-colab/discoal>`_.

Reference: Andrew D. Kern and Daniel R. Schrider. Discoal: flexible coalescent
simulations with selection. *Bioinformatics*. 2016;32(24):3839–3841.
`doi:10.1093/bioinformatics/btw556 <https://doi.org/10.1093/bioinformatics/btw556>`_.

**Next:** :doc:`Extract simulated-domain features <calc_domain>`.
