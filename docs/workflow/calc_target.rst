.. _module-calc-target:

3. Extract target features
==========================

``dasdc calc_target`` converts real genomic data into target-domain feature
maps and their corresponding position files. These outputs feed
:doc:`train` and :doc:`pred`.

Prepare the input
-----------------

Provide **phased, single-population VCF or VCF.GZ files**, split by chromosome.
Use one file per chromosome. The repository does not include ``real_data/``;
create it and supply your own files, or obtain demonstration data from
`Mendeley Data <https://data.mendeley.com/datasets/vdg2nbpc4j>`_.

Example
-------

.. code-block:: shell

   dasdc calc_target -i real_data -o real_feature

For a chromosome named ``CEU.chr2.vcf``, the outputs used in prediction are:

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Output
     - Purpose
   * - ``real_feature/CEU.chr2.vcf_featureMap.npy``
     - Target feature maps passed to ``pred --feature``.
   * - ``real_feature/CEU.chr2.vcfposInfo``
     - Matching window positions passed to ``pred --position``.


Command options
---------------
.. list-table::
   :header-rows: 1
   :widths: 29 22 49

   * - Option
     - Required / default
     - Description
   * - ``-i``, ``--input``
     - Required
     - VCF/VCF.GZ file, directory, or comma-separated files.
   * - ``-o``, ``--out``
     - Required
     - Output path for target features and positions.
   * - ``--filter``
     - ``250``
     - Discard windows with fewer SNPs. Smaller values are accepted by the CLI but have not been validated by this project.
   * - ``--window-size``
     - ``1000000`` bp
     - Genomic context used to construct each feature map.
   * - ``--window-step``
     - Window size / 20
     - Spacing between successive windows; 50,000 bp with the default window size.
   * - ``--core``
     - ``8``
     - CPU worker budget. Each input file uses up to 6 feature-calculation workers; extra cores help when processing multiple files. Multiples of 8 are not required.
   * - ``--start``
     - ``None``
     - Optional start position for extracting part of a chromosome.
   * - ``--end``
     - ``None``
     - Optional end position for extracting part of a chromosome.


Window size and reported interval
---------------------------------

With the default 1 Mb window and 50 kb step, each prediction describes
approximately the central 50 kb, using the surrounding sequence as context.
Both backends calculate the reported interval from the **central 5% of the
span between the first and last retained SNP positions** in each feature
window. The exact interval width therefore varies with SNP coverage and
chromosome boundaries.

.. list-table::
   :header-rows: 1
   :widths: 31 69

   * - Setting
     - Controls
   * - ``--window-size``
     - Feature context and the width of the central interval reported by prediction.
   * - ``--window-step``
     - Distance between successive windows. Changing the step alone does not change the reported interval width.


**Next:** :doc:`data_annotation` for training a new model, or :doc:`pred`
when reusing a compatible :doc:`trained ensemble <../models>` for the
intended population.
