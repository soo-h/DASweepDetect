.. _module-calc-domain:

2. Extract simulated features
=============================

``dasdc calc_domain`` converts the simulated sequences from :doc:`simu` into
feature maps for the simulated domain. These maps are labeled in
:doc:`data_annotation`.

Example
-------

.. code-block:: shell

   dasdc calc_domain -i simu_data -o simu_feature

Use a directory containing only simulated data, a single ms-style simulation
file, or comma-separated files. Corresponding ``.npy`` feature files are written
to ``simu_feature``.

Command options
---------------
.. list-table::
   :header-rows: 1
   :widths: 29 20 51

   * - Option
     - Required / default
     - Description
   * - ``-i``, ``--input``
     - Required
     - Simulation file, directory, or comma-separated files.
   * - ``-o``, ``--out``
     - Required
     - Output path for simulated feature maps.
   * - ``--filter``
     - ``250``
     - Reject simulated samples containing fewer than this number of SNPs.
   * - ``--core``
     - ``8``
     - CPU worker budget. Up to 8 workers per input file can be used; choose a positive value within your available CPU allocation.


**Next:** prepare real-data features with :doc:`calc_target` and label the
simulated maps with :doc:`data_annotation`. Both are needed before training.
