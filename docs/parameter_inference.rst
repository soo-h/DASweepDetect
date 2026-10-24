.. _parameter-inference:

Parameter inference and simulation priors
=========================================

Prepare mutation rate, recombination rate, selection strength and
demographic parameters for the population being analyzed before running
:doc:`workflow/simu`. Use the steps below to choose population-specific
inputs and translate them into simulation settings.

Start with relevant population studies or the curated demographic models
and genetic parameters in the `stdpopsim catalog
<https://popsim-consortium.github.io/stdpopsim-docs/stable/catalog.html>`_
([Adrion2020]_; [Lauterbur2023]_). Cite the original studies for any model
or parameter set you use, as well as the relevant stdpopsim paper.

When suitable estimates are unavailable, combine justified priors with
inference. The `Relate <https://myersgroup.github.io/relate/>`_ workflow
below estimates genealogies and demographic parameters from phased genomic
data ([Speidel2019]_; [Speidel2021]_). stdpopsim supplies published models;
Relate performs inference from data. DASDC uses discoal to generate its
training simulations.

What to prepare
---------------

.. list-table::
   :header-rows: 1
   :widths: 23 39 38

   * - Parameter
     - Evidence or estimate
     - Use in DASDC
   * - Mutation rate
     - Population-appropriate calibration and Relate rate estimates; per base per generation.
     - Set a simulation range, then convert to discoal's scaled mutation parameter.
   * - Recombination rate
     - A genetic map or an explicitly justified prior; distinguish per-base rates from map units.
     - Set the scaled recombination range for simulated fragments.
   * - Selection strength
     - A prior covering plausible selection strengths.
     - Set the ``Pa`` range for scaled selection strength.
   * - Demographic parameters
     - Effective population size through time, inferred or taken from a suitable study.
     - Convert times and relative sizes into ``en`` events.

**Example values are not population-independent defaults.** The commands
use a phased, diploid, single-population VCF and require a separate Relate
installation. They do not run as a DASDC subcommand.

1. Prepare genealogies with Relate
----------------------------------

Use one chromosome per VCF. Keep all input files on the same reference
assembly and coordinate system. Prepare:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Input
     - Meaning
   * - VCF prefix
     - ``example`` for ``example.vcf`` or ``example.vcf.gz``; omit the file extension when calling Relate.
   * - Ancestral FASTA
     - A chromosome sequence for allele polarization. A reference genome used as a proxy is an assumption and should be documented.
   * - Genetic map
     - Physical position in bp, recombination rate in cM/Mb, and cumulative genetic position in cM. A constant rate such as 1 cM/Mb is a prior, not a unit conversion.
   * - Initial population size and mutation rate
     - Initial values for genealogy inference, chosen for the study population.

The script below combines VCF conversion, population labels, input
preparation and genealogy inference. Population labels preserve sample
IDs and order from the converted ``.sample`` file and include the required
header. ``group1`` represents the single population; ``NA`` is used for
diploid samples. Consult `Relate input formats
<https://myersgroup.github.io/relate/input_data.html>`_ for other ploidies.

:download:`Download relate_prepare.sh <_static/relate_prepare.sh>` and save
it in your working directory, or use the copy in ``docs/_static/``.

.. literalinclude:: _static/relate_prepare.sh
   :language: bash

Set the paths and population-specific initial values before running it:

.. code-block:: bash

   export RELATE_ROOT=/absolute/path/to/relate
   export ANCESTOR=/absolute/path/to/ancestor_chr1.fa
   export MAP=/absolute/path/to/chr1.map
   export POP_SIZE=150
   export MUTATION_RATE=1.25e-8
   export MEMORY_GB=1

   bash relate_prepare.sh example

Here ``150``, ``1.25e-8`` and ``1`` reproduce illustrative initial settings
from the previous guide. Replace them for your data; ``MEMORY_GB`` is a
memory setting in GB. Run in a writable working directory. Relate produces
``example.anc`` and ``example.mut`` (possibly compressed), which are the
inputs to the following steps.

For multiple chromosomes, keep an identical set and order of individuals,
use names such as ``example_chr1.vcf`` and ``example_chr2.vcf``, and run the
preparation once per chromosome. This batch example expects matching
``example_chr1.fa`` and ``example_chr1.map`` files, and so on:

.. code-block:: bash

   vcf_dir=/absolute/path/to/vcf
   ancestor_dir=/absolute/path/to/ancestors
   map_dir=/absolute/path/to/maps

   for vcf in "$vcf_dir"/*.vcf "$vcf_dir"/*.vcf.gz; do
       [ -f "$vcf" ] || continue
       prefix=${vcf%.gz}
       prefix=${prefix%.vcf}
       name=${prefix##*/}
       ANCESTOR="$ancestor_dir/$name.fa" MAP="$map_dir/$name.map" \
           bash relate_prepare.sh "$prefix"
   done

2. Inspect mutation-rate estimates
----------------------------------

Run the RelateMutationRate binary directly; do not invoke it with
``bash``. For one chromosome:

.. code-block:: bash

   years_per_generation=2
   "$RELATE_ROOT/bin/RelateMutationRate" \
       --mode Avg \
       -i example \
       --years_per_gen "$years_per_generation" \
       -o example_mutation

For joint inference across chromosomes 1 and 2:

.. code-block:: bash

   years_per_generation=2
   "$RELATE_ROOT/bin/RelateMutationRate" \
       --mode Avg \
       -i example \
       --first_chr 1 --last_chr 2 \
       --years_per_gen "$years_per_generation" \
       -o example_mutation

The second example expects ``example_chr1.anc/.mut`` and
``example_chr2.anc/.mut``. Run from their directory or include the directory
in the input prefix. **Two years per generation is an example**, not a
general setting for humans or other species.

The output ``example_mutation_avg.rate`` has epochs in generations in its
first column and mutation-rate estimates in its second. The previous guide
used the minimum and maximum of the second column as simulation bounds.
Treat this as a prior-setting choice: Relate's average-rate trends can be
confounded by coalescence-rate changes, and the initial mutation-rate
calibration still matters. See the `Relate mutation-rate module
<https://myersgroup.github.io/relate/modules.html#MutationRate>`_.

.. _infer-demographic-history:

3. Infer demographic parameters
-------------------------------

Use the original ``.anc/.mut`` prefix, the corresponding population labels
and a justified mutation-rate calibration. For a single chromosome:

.. code-block:: bash

   years_per_generation=2
   threads=5
   bash "$RELATE_ROOT/scripts/EstimatePopulationSize/EstimatePopulationSize.sh" \
       -i example \
       -m "$MUTATION_RATE" \
       --years_per_gen "$years_per_generation" \
       --threads "$threads" \
       --poplabels example.poplabels \
       --seed 1 -o example_popsize

For a joint estimate across two chromosomes:

.. code-block:: bash

   years_per_generation=2
   threads=5
   bash "$RELATE_ROOT/scripts/EstimatePopulationSize/EstimatePopulationSize.sh" \
       -i example \
       --first_chr 1 --last_chr 2 \
       -m "$MUTATION_RATE" \
       --years_per_gen "$years_per_generation" \
       --threads "$threads" \
       --poplabels example_chr1.poplabels \
       --seed 1 -o example_popsize

For the joint command, both chromosomes must contain **the same samples in
the same order**, so the first chromosome's labels also describe the second.
The ``.coal`` output starts with population names and then epochs in
generations. Subsequent rows start with two population indices followed by
coalescence rates. For diploid data, **Ne = 1 / (2 × coalescence rate)**;
select the within-population row rather than assuming that the last two
lines always contain the desired population-size estimates. See the `Relate population-size
module <https://myersgroup.github.io/relate/modules.html#PopulationSizeScript>`_.

4. Set selection and recombination priors
-----------------------------------------

The following ranges preserve examples from the original guide. They are
**study-specific prior choices**, not estimates produced by Relate and not
universal recommendations by species.

.. list-table::
   :header-rows: 1
   :widths: 31 31 38

   * - Original example
     - Prior
     - Interpretation
   * - Weaker selection, illustrated with humans
     - ``s`` from 0.0001 to 0.01
     - ``Pa`` spans ``2 × N0 × 0.0001`` to ``2 × N0 × 0.01``.
   * - Stronger selection, illustrated with pigs and mosquitoes
     - ``s`` from 0.001 to 0.1
     - ``Pa`` spans ``2 × N0 × 0.001`` to ``2 × N0 × 0.1``.
   * - Recombination without a suitable direct estimate
     - Per-base ``r`` from mean mutation rate to three times that mean
     - An explicit heuristic from the previous guide; it does not infer a recombination map from mutation data.

Prefer a population-appropriate genetic map or published estimate when
available. Record the evidence and assumptions behind the selected range.

.. _simulation-parameter-scaling:

5. Transfer estimates to a simulation configuration
---------------------------------------------------

**DASDC passes configuration values to discoal without converting their
units.** In particular, do not paste a per-base mutation rate such as
``1.25e-8`` directly into ``Pt``. Let ``N0`` be the diploid reference
effective size, ``L`` the fragment length in bp, and ``t`` backward time in
generations:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Configuration entry
     - Scaled quantity
   * - ``Pt``
     - Bounds on ``theta = 4 × N0 × mu × L`` for per-base mutation rate ``mu``.
   * - ``Pr``
     - Bounds on the population-scaled recombination parameter for the entire locus, ``rho``; follow the rate convention of the supplied discoal version.
   * - ``Pa``
     - Bounds on ``alpha = 2 × N0 × s``.
   * - ``en``
     - ``en t_scaled 0 size_ratio``, where ``t_scaled = t / (4 × N0)`` and ``size_ratio = Ne(t) / N0``.

The `discoal manual <https://github.com/kr-colab/discoal/blob/master/discoaldoc.tex>`_
defines its population-scaled parameters and priors. Return to
:ref:`simulation-configuration` for all configuration entries and the five
training classes. Keep the biological estimates and the exact scaling
assumptions with your analysis records.


.. _parameter-references:

References
----------

.. [Adrion2020] Adrion JR, Cole CB, Dukler N, et al. (2020).
   A community-maintained standard library of population genetic models.
   *eLife* 9:e54967.
   `doi:10.7554/eLife.54967 <https://doi.org/10.7554/eLife.54967>`_.

.. [Lauterbur2023] Lauterbur ME, Cavassim MIA, Gladstein AL, et al. (2023).
   Expanding the stdpopsim species catalog, and lessons learned for realistic
   genome simulations. *eLife* 12:RP84874.
   `doi:10.7554/eLife.84874 <https://doi.org/10.7554/eLife.84874>`_.

.. [Speidel2019] Speidel L, Forest M, Shi S, Myers SR (2019).
   A method for genome-wide genealogy estimation for thousands of samples.
   *Nature Genetics* 51:1321–1329.
   `doi:10.1038/s41588-019-0484-x <https://doi.org/10.1038/s41588-019-0484-x>`_.

.. [Speidel2021] Speidel L, Cassidy L, Davies RW, et al. (2021).
   Inferring Population Histories for Ancient Genomes Using Genome-Wide
   Genealogies. *Molecular Biology and Evolution* 38(9):3497–3511.
   This paper describes the Relate v1.1 update, including improved
   coalescence-rate estimation.
   `doi:10.1093/molbev/msab174 <https://doi.org/10.1093/molbev/msab174>`_.
