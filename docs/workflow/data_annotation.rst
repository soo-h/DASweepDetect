.. _module-data-annotation:

4. Annotate simulated data
==========================

``dasdc data_annotation`` assigns class labels to the simulated feature maps
from :doc:`calc_domain` and prepares datasets for :doc:`train`.

Example
-------

.. code-block:: shell

   dasdc data_annotation \
       -i simu_feature \
       --config example/label_configure.txt \
       -o trainSet

Command options
---------------
.. list-table::
   :header-rows: 1
   :widths: 29 15 56

   * - Option
     - Required
     - Description
   * - ``-i``, ``--input``
     - Yes
     - Simulated ``.npy`` feature file, directory, or comma-separated files.
   * - ``--config``
     - Yes
     - Two-column label configuration file.
   * - ``-o``, ``--out``
     - Yes
     - Output directory for dataset and label arrays.


.. _label-configuration:

Label configuration
-------------------

The first column identifies the simulation name from :doc:`simu`; the second
assigns its integer class label. The supplied ``example/label_configure.txt``
contains the following mapping:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Simulation key
     - Label
     - Class
   * - ``chSel_``
     - ``0``
     - Hard selective sweep
   * - ``chLink_``
     - ``1``
     - Hard linkage
   * - ``csSel_``
     - ``2``
     - Soft selective sweep
   * - ``csLink_``
     - ``3``
     - Soft linkage
   * - ``neut``
     - ``4``
     - Neutral


.. important::

   Labels must be consecutive integers from 0 to *n* − 1 for *n* classes
   (*n* > 1). Interpret predictions using the label configuration used to
   train that model; the five-class mapping above is the supplied example.

Generated datasets
------------------
.. list-table::
   :header-rows: 1
   :widths: 18 39 43

   * - Split
     - Feature array
     - Label array
   * - Training
     - ``trainSet/trainSet.npy``
     - ``trainSet/trainSet_label.npy``
   * - Validation
     - ``trainSet/validSet.npy``
     - ``trainSet/validSet_label.npy``
   * - Test
     - ``trainSet/testSet.npy``
     - ``trainSet/testSet_label.npy``


**Next:** :doc:`Train an ensemble <train>` with these arrays and the target
features from :doc:`calc_target`.
