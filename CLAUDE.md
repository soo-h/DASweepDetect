# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

DASDC (Domain Adversarial Sweep Detection and Classification) is a bioinformatics tool that uses domain adversarial neural networks (DANN) to detect and classify selective sweeps in population genomic data. It trains on simulated data (generated via `discoal`) and adapts to real VCF data via adversarial domain adaptation, supporting 5 sweep classes: hard sweep, hard linkage sweep, soft sweep, soft linkage sweep, and neutral.

**Python versions:** The package supports Python 3.8 or newer. The legacy TensorFlow 2.7 backend requires Python 3.8-3.9; use a compatible PyTorch installation for newer Python versions.

**Hardware requirements (from README):** 8+ CPUs, 18GB+ memory, 200GB+ disk storage.

## Commands

Install dependencies:
```shell
chmod 755 discoal
python -m pip install -e .
```

The installed `dasdc` command (also available as `python -m dasdc`) exposes a six-stage pipeline. Keep the editable repository in place. `DASD.py` remains the legacy entry point.

```shell
# Step 1: Simulate training data from config files
dasdc simu -i example/simu_config/ -o simu_data

# Step 2: Feature engineering on simulated data
dasdc calc_domain -i simu_data -o simu_feature

# Step 3: Feature engineering on real VCF data
dasdc calc_target -i real_data -o real_feature

# Step 4: Label simulated features for training
dasdc data_annotation -i simu_feature --config example/label_configure.txt -o trainSet

# Step 5: Train DANN ensemble model
dasdc train --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy -t real_feature/ -o Ensemble_output

# Step 6: Predict on real data (one chromosome at a time)
dasdc pred -m Ensemble_output_ensemble/ -M 5 -f real_feature/chr1.vcf_featureMap.npy -p real_feature/chr1.vcfposInfo -o pred_result.txt
```

Key optional parameters:
- `--core`: CPU cores (default 8 for both feature-extraction stages in `dasdc`)
- `--filter`: Min SNP count to retain a sample (default 250)
- `--window-size` / `--window-step`: Control sliding window granularity for real VCF feature extraction (default 1Mbp / 50kbp)
- `-M`: Number of ensemble models for training/prediction (default 5)

Training defaults to five models; prediction requires an explicit `-M`. For PyTorch, install a CUDA-enabled build and add `--backend pytorch --device cuda` to both training and prediction. PyTorch checkpoints cannot be loaded by the TensorFlow backend.

The `example/` directory contains demo config files: `simu_config/` (5 sweep-type configs: hard sweep, hard linkage, soft sweep, soft linkage, neutral) and `label_configure.txt` (label mapping).

Packaging uses setuptools through `pyproject.toml`. Run `python -m unittest discover -s tests -v` for CLI, dispatch, and PyTorch contract tests. No linter or coverage threshold is configured. Follow `AGENTS.md` for contributor and validation requirements.

## Architecture

### Entry point and subcommand dispatch (`dasdc/`)

`dasdc/cli.py` defines the `argparse` interface. `dasdc/runner.py` resolves paths and invokes the stage script with the current Python interpreter using `subprocess.run(check=True)`, preserving failures. It selects the TensorFlow or PyTorch training/prediction scripts and checks backend availability. `DASD.py` retains the legacy dispatch implementation.

### Core pipeline scripts (in `DASD/`)

| Script | Purpose |
|---|---|
| `simudata_gen.py` | Reads config files, builds `discoal` command lines, runs coalescent simulations |
| `simudata_to_feature.py` | Converts simulated ms-style output to feature matrices (summary statistics). Manages CPU allocation with a `process_saver` scheduler. |
| `vcf_to_featureMap.py` | Converts real VCF data to feature matrices. Splits chromosomes into windows, computes population genetic statistics in parallel subprocesses. |
| `label_data.py` | Splits feature data into train/valid/test sets (80/10/10) with labels from a config file. |
| `DANN_train.py` | Trains an ensemble of DANN models (default 5). Uses early stopping on validation accuracy. Outputs model checkpoints and training logs. |
| `pred_ensemble.py` | Loads an ensemble of trained models, averages their predictions, outputs sweep classification results per genomic window. |
| `DANN_train_torch.py` | Trains the optional PyTorch ensemble and saves `model.pt` checkpoints, training logs, and ensemble metadata. |
| `pred_ensemble_torch.py` | Averages predictions from PyTorch checkpoints and writes genomic interval predictions. |

### DANN model architecture (`DASD/util/DANN_.py`)

Three components composed into a `DANN` model (subclass of `tf.keras.Model`):

1. **`feature_extracter`** — 2D CNN (Conv2D + MaxPooling2D layers) operating on (samples, statistics, windows) input tensors, flattens to a feature vector.
2. **`classifier`** — Dense layers (256→256→128→5) with batch norm, dropout, and softmax output for the 5 sweep classes.
3. **`Discriminator`** — Dense layers (256→128→1) with sigmoid output for domain classification (source=simulated vs target=real).

The discriminator receives features passed through a **gradient reversal layer** (`gradient_reversal` in `util/loss.py`), which negates gradients during backprop scaled by an `alpha` parameter that increases over training.

`DASD/util/torch_dann.py` implements the corresponding PyTorch model and gradient reversal. Training and prediction must use the same backend.

### Feature computation sub-packages

- **`DASD/script_simu_fev/`** — Summary statistics for simulated data: SFS, haplotype frequencies, allele frequencies, SAFE, HAF, iHS, nSL, diHH.
- **`DASD/script_real_fev/`** — Same statistics adapted for real VCF data, plus EHH-based statistics computed on real genotypes.

### Utility modules (`DASD/util/`)

| Module | Role |
|---|---|
| `loss.py` | Gradient reversal custom gradient, domain loss (binary cross-entropy), early stopping closure |
| `pretreatment.py` | Max-min normalization across the feature dimension |
| `train_utils.py` | Path parsing helpers for model names and target data directories |
| `check_tools.py` | Input validation (file paths, config format, parameter checks) |
| `process_control.py` | `para_run()` for managing parallel multiprocessing pools |
| `window_tools.py` | Sliding window logic for splitting chromosomes, ms-format parsers |
| `tools_feature.py` | `loadstastic()` — assembles individual statistic arrays into the final 3D feature map |
| `stas_compute.py` | Statistical computation primitives |

### Data flow

Input data is always 3D arrays of shape `(samples, 40 statistics, windows)`. The 40 statistics come from population genetic summary statistics computed over sliding windows. Labels are integers 0–4 representing the 5 sweep categories. Max-min normalization is applied across the feature (statistic) axis before training and prediction.

### External dependencies

- **`discoal`** — Precompiled x86-64 Linux binary for coalescent simulations with selection (max fragment length 220kbp; recompile for longer). Source: https://github.com/kr-colab/discoal
- **`Relate`** (optional, for parameter inference) — Used to estimate mutation rates and demographic history from VCF data before running DASDC. Documented in `Parameter_Inference.md`.
