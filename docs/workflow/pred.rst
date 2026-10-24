.. _module-pred:

.. _predict-sweep-classes:

6. Predict selective sweep classes
==================================

``dasdc pred`` applies an ensemble to the feature maps of one chromosome.
Use an ensemble from :doc:`train` or an existing :doc:`trained ensemble
<../models>` for the intended population, together with compatible features
and positions from :doc:`calc_target`.

Example
-------

.. code-block:: shell

   mkdir -p pred_res
   dasdc pred \
       -m Ensemble_CEU_ensemble/ -M 5 \
       -f real_feature/CEU.chr2.vcf_featureMap.npy \
       -p real_feature/CEU.chr2.vcfposInfo \
       -o pred_res/CEU.chr2.pred.txt

The default backend is TensorFlow. Create the output directory before
running prediction; the command writes the file but does not create its
parent directories.

.. note::

   **GPU execution:** TensorFlow automatically uses an available compatible
   GPU for supported operations; see :ref:`tensorflow-gpu`. The command
   above needs no additional device option.

   **Optional PyTorch backend:** for a PyTorch ensemble, follow the
   :ref:`PyTorch installation <pytorch-backend>` and append
   ``--backend pytorch``. For GPU execution, also add ``--device cuda``.
   Keep the same feature and position inputs and the default prediction
   settings.

Command options
---------------
.. list-table::
   :header-rows: 1
   :widths: 29 22 49

   * - Option
     - Required / default
     - Description
   * - ``-m``, ``--model``
     - Required
     - Directory containing the ensemble members.
   * - ``-M``
     - Required
     - Number of models; there is no CLI default. TensorFlow currently requires 5. A PyTorch directory must contain exactly this many ``model.pt`` checkpoints.
   * - ``-f``, ``--feature``
     - Required
     - Target feature array, e.g. ``CEU.chr2.vcf_featureMap.npy``.
   * - ``-p``, ``--position``
     - Required
     - Matching position file, e.g. ``CEU.chr2.vcfposInfo``.
   * - ``-o``, ``--out``
     - Required
     - Prediction output file.
   * - ``--backend``
     - ``tensorflow``
     - Choose ``tensorflow`` or ``pytorch`` to match the ensemble's training backend.


.. important::

   Predict each chromosome separately. For ten chromosomes, run this command
   ten times with the matching feature file, position file and output path.
   TensorFlow and PyTorch checkpoints are not interchangeable.

The output contains genomic intervals, predicted labels and ensemble
probabilities. See :doc:`../outputs` for the column definitions, a worked
example and filtering recommendations.
