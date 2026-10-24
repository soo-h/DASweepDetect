:orphan:

User guide
==========

Start with the :doc:`overview <index>` for the method and usage entry points. The section links below preserve the original manual address.

Configuration Required for Operation
------------------------------------

:doc:`installation` — Check platform, hardware and backend requirements.

Overview
--------

:doc:`index` — Read the prediction examples and model architecture.

Getting Started
---------------

:doc:`installation` — Set up an environment and install DASDC.

Usage
-----

:doc:`workflow/overview` — Detect selective sweeps from scratch, including model training.

Step 1: Simulate Dataset for Model Training
-------------------------------------------

:doc:`workflow/simu` — Generate simulated training sequences.

Step 2: Feature Engineering for Simulated Dataset
-------------------------------------------------

:doc:`workflow/calc_domain` — Extract simulated-domain features.

Step 3: Feature Engineering for Real Genomic Data
-------------------------------------------------

:doc:`workflow/calc_target` — Extract target-domain features and positions.

Step 4: Data Labeling for Simulated Dataset
-------------------------------------------

:doc:`workflow/data_annotation` — Label features and prepare dataset splits.

Step 5: Model Training
----------------------

:doc:`workflow/train` — Train a domain-adaptive ensemble.

Step 6: Prediction
------------------

:doc:`workflow/pred` — Predict selective sweep classes for each chromosome.

Output
------

:doc:`outputs` — Interpret output columns, labels and probabilities.

Available Models
----------------

:doc:`models` — Detect selective sweeps with an existing population-specific model.

FAQ
---

:doc:`faq` — Find out where to report a problem.
