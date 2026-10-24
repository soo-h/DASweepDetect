Trained models
==============

This page covers inference with an already-trained, population-specific DASDC
ensemble.

Training in the study
---------------------

`Section 2.8 of the DASDC paper
<https://pmc.ncbi.nlm.nih.gov/articles/PMC11005742/>`_ describes separate
models trained for human CEU, Large White pigs (LW), and Burkina Faso
*Anopheles* (BFS), using their population-specific genetic parameters.
Training aligns labeled simulations with real target-domain features.

For a new target population, follow the :ref:`six-module workflow
<workflow-modules>` using its parameters and target-domain data. Use a
saved ensemble for the population and feature setup on which it was trained;
performance on other populations or species requires separate evaluation.

Model catalog
-------------

The author's `Mendeley Data record (v4)
<https://data.mendeley.com/datasets/vdg2nbpc4j/4>`_ describes
``available_models`` as models already trained for specific species. The paths
below follow the original repository manual and refer to that downloaded
collection, not files bundled with the Git clone.

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Species
     - Model / population
     - Location in the collection
   * - *Homo sapiens*
     - **CEU** — Utah residents with Northern and Western European ancestry
     - ``available_models/Homo_sapiens/CEU``
   * - *Sus scrofa domestica*
     - **LW** — Large White pig
     - ``available_models/Sus_scrofa/LW``
   * - *Anopheles gambiae*
     - **BFS** — Burkina Faso population
     - ``available_models/Anopheles_gambiae/BFS``


.. _two-step-workflow:

Prediction with a saved ensemble
--------------------------------

Once a matching trained ensemble is available,
:doc:`extract target features <workflow/calc_target>` and run
:doc:`prediction <workflow/pred>` with its saved parameters. Match the
population, feature construction, label mapping and backend to that ensemble.

1. Extract real-data features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supply phased, single-population VCF/VCF.GZ data split by chromosome:

.. code-block:: shell

   dasdc calc_target -i real_data -o real_feature

2. Predict each chromosome
~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace ``MODEL_PATH`` with the directory containing the ensemble members:

.. code-block:: shell

   mkdir -p pred_res
   dasdc pred \
       -m MODEL_PATH -M 5 \
       -f real_feature/CEU.chr2.vcf_featureMap.npy \
       -p real_feature/CEU.chr2.vcfposInfo \
       -o pred_res/CEU.chr2.pred.txt

This example uses the default TensorFlow backend, which requires five
members for prediction and automatically uses an available compatible GPU
for supported operations (see :ref:`tensorflow-gpu`). For an ensemble
trained with the :ref:`optional PyTorch backend <pytorch-backend>`, append
``--backend pytorch`` and use its actual model count. Add ``--device cuda``
for PyTorch GPU execution. The archived models should not be assumed to
contain PyTorch checkpoints.

.. important::

   Predict each chromosome separately with its corresponding feature and
   position files. Match the population, training backend and feature setup
   to the ensemble you selected.

See :doc:`outputs` to interpret the resulting labels and probabilities.
