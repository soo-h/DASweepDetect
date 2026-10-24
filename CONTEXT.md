# DASDC Selective Sweep Analysis

This context defines the shared language for detecting and classifying selective-sweep signals in a single population. It distinguishes biological claims, genomic analysis units, domain-adaptation data, and model-reported candidates.

## Language

### Biological Context

**Target Population**:
The single population whose genome is being analyzed for selective-sweep signals.
_Avoid_: Species, group, target dataset

**Individual**:
One diploid organism represented in the target population's genomic data.
_Avoid_: Sample

**Haplotype**:
One phased chromosome sequence contributed by an individual.
_Avoid_: Sample, individual

**Population-Genetic Parameters**:
The mutation rate, recombination rate, selection strength, and demographic history used to characterize a target population.
_Avoid_: Population settings, simulation settings

### Sweep Classes

**Selective Sweep**:
The genomic footprint produced when positive selection increases the frequency of a favorable allele and its associated haplotypes.
_Avoid_: Selection event, significant region

**Hard Sweep**:
A selective sweep dominated by one high-frequency haplotype arising from a single favored origin.
_Avoid_: Classic sweep

**Linked Hard Sweep**:
A focal interval carrying a linkage signal from a hard sweep whose selected site lies outside the focal interval but within the analysis window.
_Avoid_: Hard linkage sweep, hard-linked sweep

**Soft Sweep**:
A selective sweep in which multiple favored haplotypes rise to moderate or high frequency, commonly from standing variation or recurrent mutation.
_Avoid_: Partial sweep

**Linked Soft Sweep**:
A focal interval carrying a linkage signal from a soft sweep whose selected site lies outside the focal interval but within the analysis window.
_Avoid_: Soft linkage sweep, soft-linked sweep

**Neutral**:
A focal interval assigned to the class with no modeled selective-sweep event in its analysis window; it does not imply the absence of other evolutionary forces.
_Avoid_: No evolution, negative selection

**Sweep Class**:
Exactly one of Hard Sweep, Linked Hard Sweep, Soft Sweep, Linked Soft Sweep, or Neutral.
_Avoid_: Sweep type, label meaning

**Sweep Signal**:
A pattern of population-genetic variation consistent with a selective sweep, but not by itself proof of a biological selection event.
_Avoid_: Confirmed sweep, significant sweep

### Genomic Analysis Units

**Genomic Window**:
A position-indexed region of a real chromosome evaluated as one observation in the sliding-window analysis.
_Avoid_: Sample, sequence

**Analysis Window**:
The complete genomic span used to derive the population-genetic evidence for one prediction.
_Avoid_: Focal window, prediction interval

**Focal Interval**:
The central part of an analysis window that receives the reported sweep class.
_Avoid_: Selected region, analysis window, prediction region

**Window Step**:
The genomic distance between the starting positions of consecutive analysis windows.
_Avoid_: Window size, focal-interval size

**Feature Map**:
The model-ready representation of population-genetic summary statistics derived from an analysis window.
_Avoid_: Feature matrix, sample

### Domains and Observations

**Simulation Replicate**:
One independently simulated genomic fragment associated with one sweep class.
_Avoid_: Sample, individual, genomic window

**Source Domain**:
The labeled collection of feature maps derived from simulation replicates.
_Avoid_: Simulation dataset, training population

**Target Domain**:
The unlabeled collection of feature maps derived from genomic windows in the target population and used for domain adaptation and prediction.
_Avoid_: Test domain, real-data sample

**Domain Mismatch**:
A difference between the source-domain and target-domain feature distributions that can reduce transfer of sweep-class boundaries.
_Avoid_: Label mismatch, prediction error

**Domain Adaptation**:
The alignment of source-domain and target-domain representations while retaining information that distinguishes sweep classes.
_Avoid_: Data calibration, model fine-tuning

### Reported Results

**Prediction Score**:
A model output used to rank support for a sweep class; it is not a calibrated probability, p-value, or guarantee of biological significance.
_Avoid_: Probability, significance score, confidence level

**Sweep Candidate**:
A focal interval prioritized from model predictions for downstream investigation, without claiming that selection has been independently validated.
_Avoid_: Confirmed sweep, significant locus, causal locus

**Exploratory Candidate**:
A sweep candidate retained by a heuristic prioritization rule rather than a calibrated significance procedure.
_Avoid_: Significant candidate, validated candidate
