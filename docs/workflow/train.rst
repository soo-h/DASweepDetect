.. _module-train:

5. Train an ensemble
====================

``dasdc train`` learns a population-specific ensemble from labeled simulated
data and real target-domain features. Prepare the arrays with
:doc:`data_annotation` and the target features with :doc:`calc_target`.

Example
-------

TensorFlow is the default backend and requires Python 3.8–3.9:

.. code-block:: shell

   dasdc train \
       --train-data trainSet/trainSet.npy \
       --train-label trainSet/trainSet_label.npy \
       --valid-data trainSet/validSet.npy \
       --valid-label trainSet/validSet_label.npy \
       --test-data trainSet/testSet.npy \
       --test-label trainSet/testSet_label.npy \
       -t real_feature/ -M 5 \
       -o Ensemble_CEU

.. note::

   **GPU execution:** TensorFlow automatically uses an available compatible
   GPU for supported operations; see :ref:`tensorflow-gpu`. The command
   above needs no additional device option.

   **Optional PyTorch backend:** after the :ref:`PyTorch installation
   <pytorch-backend>`, append ``--backend pytorch``. For GPU execution, also
   add ``--device cuda``. Keep the same inputs and the default training
   settings.

Required inputs and output
--------------------------
.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Option
     - Description
   * - ``--train-data``
     - Training feature array: ``trainSet/trainSet.npy``.
   * - ``--train-label``
     - Training labels: ``trainSet/trainSet_label.npy``.
   * - ``--valid-data``
     - Validation feature array: ``trainSet/validSet.npy``.
   * - ``--valid-label``
     - Validation labels: ``trainSet/validSet_label.npy``.
   * - ``--test-data``
     - Test feature array: ``trainSet/testSet.npy``.
   * - ``--test-label``
     - Test labels: ``trainSet/testSet_label.npy``.
   * - ``-t``, ``--target``
     - Target feature file, directory, or comma-separated files from ``calc_target``.
   * - ``-o``, ``--out``
     - Model output prefix; ``Ensemble_CEU`` produces ``Ensemble_CEU_ensemble/``.


Ensemble and backend options
----------------------------
.. list-table::
   :header-rows: 1
   :widths: 29 20 51

   * - Option
     - Default
     - Description
   * - ``-M``
     - ``5``
     - Number of ensemble members; five is recommended.
   * - ``--backend``
     - ``tensorflow``
     - Choose ``tensorflow`` or ``pytorch``; both support CPU and GPU execution. Prediction must use the same backend.
   * - ``-s``, ``--save``
     - ``0``
     - PyTorch: 0 retains the best checkpoint, 1 retains every epoch. The TensorFlow CLI currently retains intermediate model directories with either value.


Saved ensemble
--------------

For ``-o Ensemble_CEU``, the ensemble is stored under
``Ensemble_CEU_ensemble/``. The default TensorFlow backend saves one model
directory per ensemble member. The optional PyTorch backend saves:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Artifact
     - Purpose
   * - ``model_N/model.pt``
     - Checkpoint for each ensemble member.
   * - Training log
     - Tab-separated log alongside each member's checkpoint.
   * - ``ensemble.json``
     - Input shape, backend, PyTorch version and validation/test metrics.


**Next:** :doc:`pred` using the resulting ensemble and matching backend.
