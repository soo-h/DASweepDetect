# DASDC: Detection and classification of selective sweeps

1. [Introduction](#1-introduction)
2. [Installation and usage](#2-installation-and-usage)
3. [Trained models and example data](#3-trained-models-and-example-data)
4. [Citation](#4-citation)
5. [Contact](#5-contact)
6. [License](#6-license)

## 1. Introduction

**DASDC**, short for **D**omain **A**dversarial **S**weep **D**etection and **C**lassification, is a population-genomics tool for **detecting and classifying selective sweeps within a single population**. It identifies candidate genomic regions and infers whether they have undergone hard or soft selective sweeps, together with the corresponding probabilities.

DASDC learns population genomic signatures of selection from simulated data, given the scarcity of selection signals in real genomic data. Specifically, DASDC uses a **domain-adversarial learning framework** to align feature representations between simulated and real genomic data while preserving information relevant to selective sweep classification, improving generalization to real data. The trained model is then applied to phased genomic data in VCF format from the corresponding population to detect and classify selective sweeps.

<img src="docs/_static/overview-original.png" alt="DASDC workflow and model architecture" width="760" />

*DASDC workflow and model architecture.*

<img src="docs/_static/paper/sweep-predictions.png" alt="Hard and soft selective sweep predictions in the LW pig population: NR6A1 and FSHβ" width="700" />

*Hard and soft selective sweep predictions in the LW pig population.*

## 2. Installation and usage

For installation instructions and usage examples, visit the
[DASDC documentation](https://dasweepdetect.readthedocs.io/en/latest/).

The manual covers [detection from scratch](https://dasweepdetect.readthedocs.io/en/latest/workflow/overview.html),
[detection with an existing model](https://dasweepdetect.readthedocs.io/en/latest/models.html#two-step-workflow),
[parameter inference](https://dasweepdetect.readthedocs.io/en/latest/parameter_inference.html),
and [prediction outputs](https://dasweepdetect.readthedocs.io/en/latest/outputs.html).

DASDC runs on Linux x86-64. TensorFlow is the default backend and PyTorch is
optional; both support CPU and GPU execution. See the
[installation guide](https://dasweepdetect.readthedocs.io/en/latest/installation.html)
for compatible Python versions and GPU requirements.

## 3. Trained models and example data

Population-specific models are available for human CEU, Large White pigs
(LW), and Burkina Faso *Anopheles gambiae* (BFS). Model and example data
resources are hosted on [Mendeley Data](https://data.mendeley.com/datasets/vdg2nbpc4j/4).

To detect selective sweeps with an existing model, follow the
[existing-model detection guide](https://dasweepdetect.readthedocs.io/en/latest/models.html).
Use the model for its intended population, with matching feature construction
and backend. For a new target population, follow the complete workflow to
train a population-specific model.

## 4. Citation

If you use DASDC, please cite:

Song H, Chu J, Li W, et al. A Novel Approach Utilizing Domain Adversarial
Neural Networks for the Detection and Classification of Selective Sweeps.
*Advanced Science* 11(14):2304842 (2024).
[doi:10.1002/advs.202304842](https://doi.org/10.1002/advs.202304842)

The simulation workflow uses discoal:

Kern & Schrider. discoal: flexible coalescent simulations with selection.
*Bioinformatics* (2016).
[doi:10.1093/bioinformatics/btw556](https://doi.org/10.1093/bioinformatics/btw556)

For stdpopsim and Relate citations, see the
[parameter inference references](https://dasweepdetect.readthedocs.io/en/latest/parameter_inference.html#parameter-references).

## 5. Contact

Report problems or requests through
[GitHub Issues](https://github.com/soo-h/DASweepDetect/issues).
The DASDC Communication QQ Group is **602055867**.

## 6. License

DASDC is released under the [MIT License](LICENSE).
Paper-derived figures are adapted from [Song et al. (2024)](https://doi.org/10.1002/advs.202304842),
© 2024 The Authors, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
