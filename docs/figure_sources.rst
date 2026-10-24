:orphan:

.. _figure-sources:

Figure sources and adaptations
==============================

The paper-derived figures in the overview are adapted from Song et al.
(2024), Advanced Science 11(14):2304842,
`doi:10.1002/advs.202304842 <https://doi.org/10.1002/advs.202304842>`_.
The article and its figures are © 2024 The Authors and licensed under
`Creative Commons Attribution 4.0 <https://creativecommons.org/licenses/by/4.0/>`_.

Images were extracted from the published PDF downloaded on 24 October 2026
through the NLM PubMed Central Article Datasets on AWS. See the
`PMC article <https://pmc.ncbi.nlm.nih.gov/articles/PMC11005742/>`_.

.. list-table::
   :header-rows: 1
   :widths: 24 27 49

   * - Documentation figure
     - Original source
     - Adaptation
   * - :numref:`sweep-predictions`
     - Paper Fig. 7b; PDF page 10
     - NR6A1 and FSHβ locus panels cropped and arranged horizontally. Headers and genomic position units added; plotted points, axes and probability labels retained.
   * - :numref:`dasdc-overview-figure`
     - Original repository overview image
     - Preserved without editing; the same image appeared in the previous manual.
   * - :numref:`domain-alignment`
     - Paper Figs. 1b and 3a; PDF pages 3 and 5
     - Complete PCA panels with legends and marginal histograms cropped and placed side by side. Original panel letters removed outside plots; new headers added. Raw panel uniformly resized. Simulated-data contours, marginal histograms and legend swatch in the learned-representation panel recolored from orange to red to match the raw-data panel; blue real-data marks retained. Paper figure numbers removed from the panel subtitles; axis values unchanged.
   * - :numref:`workflow-data-flow`
     - Documentation workflow diagram
     - A command-level guide to the six DASDC modules, drawn for this manual.

On narrow screens the same panels stack vertically for readable labels.

PDF images were converted from print CMYK to web RGB where needed.
No plotted values, probabilities, axis scales or scientific annotations
were changed. The two PCA panels describe different feature spaces and
have separate axes; their coordinates must not be compared directly.

The :download:`figure provenance manifest <_static/paper/sources.json>`
records the source PDF URL, SHA-256 checksums, crop coordinates and changes.
It allows the figures to be traced to the published originals without
adding the full paper PDF to the repository.
