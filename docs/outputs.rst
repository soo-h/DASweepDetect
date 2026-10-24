Outputs and interpretation
==========================

The :doc:`prediction module <workflow/pred>` writes a tab-separated text file
with a header and one row per predicted genomic window.

Prediction columns
------------------
.. list-table::
   :header-rows: 1
   :widths: 20 57 23

   * - Column
     - Meaning
     - Example
   * - ``pos_left``
     - Left endpoint of the reported interval, in bp.
     - ``485078``
   * - ``pos_right``
     - Right endpoint of the reported interval, in bp.
     - ``535068``
   * - ``class``
     - Integer label of the class with the highest ensemble probability.
     - ``4``
   * - ``prob``
     - Highest class probability after averaging ensemble predictions.
     - ``0.7978562``
   * - ``all_prob``
     - Comma-separated ensemble probabilities, ordered by class label (0 through n − 1).
     - Five values for the supplied five-class setup.


Read a prediction
-----------------

The first row of ``example/pred_res/pred_res_chr2.txt`` reports the interval
``485078–535068`` with predicted label ``4`` and probability ``0.7978562``.
With the supplied :ref:`label configuration <label-configuration>`, label 4
means **neutral**. Its per-class values are:

.. list-table::
   :header-rows: 1
   :widths: 15 45 40

   * - Label
     - Class
     - Probability
   * - ``0``
     - Hard selective sweep
     - ``0.00057559146``
   * - ``1``
     - Hard linkage
     - ``0.0027355235``
   * - ``2``
     - Soft selective sweep
     - ``0.019203266``
   * - ``3``
     - Soft linkage
     - ``0.1796294``
   * - ``4``
     - Neutral
     - ``0.7978562``


Always use the label configuration associated with the trained model. A custom
configuration may assign different meanings to the integer labels.

Interval width and prediction spacing
-------------------------------------

Both backends report the **central 5% of the span between the first and
last retained SNP positions** in each feature window. With a well-covered
1 Mb window, this is approximately 50 kb. ``--window-step`` controls the
spacing between windows; SNP coverage and chromosome boundaries also affect
the exact reported interval. See :doc:`workflow/calc_target` for details.

Prioritize candidate regions
----------------------------
.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Result
     - Recommended use
     - Reason / trade-off
   * - Soft selective sweep calls
     - Prioritize the highest-scoring 5% of windows classified as soft selective sweeps for exploratory follow-up.
     - Soft selective sweep signals are more heterogeneous and less separable than hard selective sweep signals.
   * - Hard selective sweep + hard linkage
     - Scores may be combined for visualization.
     - Can increase detection power at the cost of precision.
   * - Soft selective sweep + soft linkage
     - Keep these scores separate.
     - Combining them can carry false-positive soft-linkage signals into reported soft selective sweep candidates.


Demographic effects, heterogeneous recombination rates, missing genomic regions
and simulation-to-real domain mismatch can cause neutral or other classes to
be predicted as soft selective sweeps or soft linkage. Treat the filtering guidance as
candidate prioritization, not a calibrated false-discovery threshold.
