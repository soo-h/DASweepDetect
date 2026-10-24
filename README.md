# DASDC

*Domain Adversarial Sweep Detection and Classification*

DASDC is a deep learning tool that uses domain adversarial neural networks (DANN) to detect and classify selective sweeps in population genomic data. By incorporating adversarial adaptation between simulated training data and real data, it improves generalization under domain mismatch, as described in the [DASDC paper](https://doi.org/10.1002/advs.202304842).

## Requirements

- **Platform:** Linux (x86-64)
- **Python:** 3.8 or newer
- **TensorFlow backend:** Python 3.8-3.9 with TensorFlow 2.7
- **PyTorch backend:** PyTorch 2.2 or newer; a CUDA-enabled build is required for GPU training
- **Hardware:** 8+ CPUs, 18 GB+ memory, 200 GB+ disk; a CUDA GPU is recommended for PyTorch training

## Quick Start

The repository includes simulation and label configurations, but not `real_data/`. Before running the pipeline, supply phased, single-population VCF or VCF.GZ files split by chromosome. Larger demonstration files and intermediate results are available from [Mendeley Data](https://data.mendeley.com/datasets/vdg2nbpc4j).

```shell
# TensorFlow workflow: use Python 3.8 or 3.9.
# Keep this clone in place because the editable installation calls its scripts.
chmod 755 discoal
python -m pip install -e .

# Run the 6-step pipeline
dasdc simu -i example/simu_config/ -o simu_data
dasdc calc_domain -i simu_data -o simu_feature
dasdc calc_target -i real_data -o real_feature
dasdc data_annotation -i simu_feature --config example/label_configure.txt -o trainSet
dasdc train \
    --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy \
    --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy \
    --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy \
    -t real_feature/ -o Ensemble_output
dasdc pred -m Ensemble_output_ensemble/ -M 5 -f real_feature/chr1.vcf_featureMap.npy -p real_feature/chr1.vcfposInfo -o pred_result.txt
```

Each command can also be invoked as `python -m dasdc <command>`. The legacy
`python3.8 DASD.py <command>` entry point remains available for compatibility.
Because this installation is editable, do not move or delete the cloned repository
without reinstalling DASDC.

TensorFlow prediction currently requires `-M 5` and an ensemble directory containing exactly five sub-model directories.

`--window-size` controls the genomic context used for each prediction;
`--window-step` controls the distance between successive windows. With the
default 1 Mb window and 50 kb step, each prediction describes the central
50 kb interval using 475 kb of context on each side. The reported interval
is the central 5% of the window, so changing the step alone does not change
its width.

## PyTorch GPU Backend

Install a CUDA-enabled PyTorch build that matches the system driver. For example,
the following installs PyTorch 2.2.2 for CUDA 12.1; use the
[official PyTorch selector](https://pytorch.org/get-started/locally/) for other
CUDA or Python versions.

```shell
python -m pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu121
python -m pip install -e .
```

Train and predict with the same backend:

```shell
dasdc train \
    --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy \
    --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy \
    --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy \
    -t real_feature/ -M 5 -o Ensemble_output \
    --backend pytorch --device cuda

dasdc pred \
    -m Ensemble_output_ensemble/ -M 5 \
    -f real_feature/chr1.vcf_featureMap.npy \
    -p real_feature/chr1.vcfposInfo -o pred_result.txt \
    --backend pytorch --device cuda
```

PyTorch training defaults to 50 epochs, batch size 32, SGD learning rate 0.01,
five-epoch early stopping, and CUDA automatic mixed precision. Select a visible
GPU with `--device cuda:1`; use `--device cpu --no-amp` only for debugging.
Checkpoints are stored as `MODEL_PREFIX_ensemble/model_N/model.pt` and are not
compatible with TensorFlow prediction.

## Documentation

The user manual is configured for automatic builds and hosting on
**[Read the Docs](https://readthedocs.org/)**. Readers do not need to build it
locally. The project's public documentation URL will be added here after the
repository is connected and its first build succeeds.

For maintainers, see the [publishing guide](docs/PUBLISHING.md) for initial
Read the Docs setup, automatic updates, and optional local previews.

See **[Parameter_Inference.md](Parameter_Inference.md)** for guidance on estimating mutation rates, demographic history, recombination rates, and selection strength using Relate.

## Available Models

Pre-trained models for specific populations are available at [Mendeley Data](https://data.mendeley.com/datasets/vdg2nbpc4j).

| Species | Population | Location |
|---|---|---|
| *Homo sapiens* | CEU (European) | `available_models/Homo_sapiens/CEU` |
| *Sus scrofa domestica* | Large White pig | `available_models/Sus_scrofa/LW` |
| *Anopheles gambiae* | Burkina Faso | `available_models/Anopheles_gambiae/BFS` |

## Support

Report problems through the [GitHub issue tracker](https://github.com/soo-h/DASweepDetect/issues).
The upstream project also lists DASDC Communication QQ Group: **602055867**.

## References

- Song H, Chu J, Li W, et al. (2024). A Novel Approach Utilizing Domain Adversarial Neural Networks for the Detection and Classification of Selective Sweeps. *Advanced Science*. [doi:10.1002/advs.202304842](https://doi.org/10.1002/advs.202304842)
- Kern & Schrider (2016) — discoal: [doi:10.1093/bioinformatics/btw556](https://doi.org/10.1093/bioinformatics/btw556)

## License

See [LICENSE](LICENSE) for details.
