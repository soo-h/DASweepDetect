DASDC: Detection and classification of selective sweeps
=======================================================

**DASDC**, short for **D**\ omain **A**\ dversarial **S**\ weep **D**\ etection and **C**\ lassification, is a population-genomics tool for **detecting and classifying selective sweeps within a single population**. It identifies candidate genomic regions and infers whether they have undergone hard or soft selective sweeps, together with the corresponding probabilities (:numref:`sweep-predictions`).

.. _prediction-examples:

Prediction examples
-------------------

.. _sweep-predictions:

.. figure:: _static/paper/sweep-predictions.png
   :alt: LW pig selective sweep predictions: NR6A1 is a hard selective sweep with probability 0.992 and FSH beta is a soft selective sweep with probability 0.867. The plots show prediction scores along each genomic region.
   :class: paper-figure prediction-figure

   Hard and soft selective sweep predictions in the LW pig population.
   (A) NR6A1, hard selective sweep; (B) FSHβ, soft selective sweep.

.. _model-architecture:

Model architecture
------------------

DASDC learns population genomic signatures of selection from simulated data, given the scarcity of selection signals in real genomic data. Specifically, DASDC uses a **domain-adversarial learning framework** to align feature representations between simulated and real genomic data while preserving information relevant to selective sweep classification, improving generalization to real data (:numref:`dasdc-overview-figure`, :numref:`domain-alignment`). The trained model is then applied to phased genomic data in VCF format from the corresponding population to detect and classify selective sweeps.

.. Original overview figure retained byte for byte from the repository manual.
   Source: https://github.com/soo-h/DASweepDetect/assets/74720083/a1205262-6a17-4ec3-84fb-5e82bb92ca4c

.. _dasdc-overview-figure:

.. figure:: _static/overview-original.png
   :alt: DASDC workflow linking population-specific simulations and real VCF features to a shared feature extractor, selective sweep label predictor and domain discriminator.
   :align: center
   :class: overview-figure

   DASDC workflow and model architecture. A shared feature extractor
   supports selective sweep classification and domain alignment.

.. _domain-alignment:

.. figure:: _static/paper/domain-alignment.png
   :alt: Separate PCA plots of simulated and real CEU data: raw summary statistics in panel A separate the domains, while learned representations in panel B show more overlap. Each panel includes a legend and marginal histograms.
   :class: paper-figure alignment-figure

   Alignment of simulated and real CEU data. (A) Raw summary statistics;
   (B) learned representations. PCA axes are computed separately for each panel.

.. _choose-your-path:

Start here
----------

* :doc:`Install <installation>`
* :doc:`Detect selective sweeps from scratch <workflow/overview>`
* :ref:`Detect selective sweeps with an existing model <two-step-workflow>`

.. _about-the-method:

Citation and support
--------------------

For the model architecture, evaluation and applications to real genomic
data, see the `DASDC paper <https://doi.org/10.1002/advs.202304842>`_.

If you use DASDC, please cite:

   Hui Song, Jinyu Chu, Wangjiao Li, *et al.* A Novel Approach Utilizing Domain
   Adversarial Neural Networks for the Detection and Classification of
   Selective Sweeps. *Advanced Science*. 2024;11(14):e2304842.
   `doi:10.1002/advs.202304842 <https://doi.org/10.1002/advs.202304842>`_.

Report bugs and usage problems through the
`GitHub issue tracker <https://github.com/soo-h/DASweepDetect/issues>`_.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Get started

   Overview <self>
   installation
   Detect selective sweeps from scratch <workflow/overview>
   Detect selective sweeps with an existing model <models>

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Workflow modules

   1. Simulation <workflow/simu>
   2. Simulated features <workflow/calc_domain>
   3. Target features <workflow/calc_target>
   4. Data annotation <workflow/data_annotation>
   5. Model training <workflow/train>
   6. Prediction <workflow/pred>

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Reference

   parameter_inference
   outputs
   faq
