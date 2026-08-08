# DASDC

*Domain Adversarial Sweep Detection and Classification*

DASDC is a deep learning tool that uses domain adversarial neural networks (DANN) to detect and classify selective sweeps in population genomic data. By incorporating adversarial adaptation between simulated training data and real data, it improves generalization under domain mismatch, as described in the [DASDC paper](https://doi.org/10.1002/advs.202304842).

## Requirements

- **Platform:** Linux (x86-64)
- **Python:** 3.8 (legacy; use an isolated environment)
- **Hardware:** 8+ CPUs, 18 GB+ memory, 200 GB+ disk

## Quick Start

The repository includes simulation and label configurations, but not `real_data/`. Before running the pipeline, supply single-population VCF or VCF.GZ files split by chromosome. Larger demonstration files and intermediate results are available from [Mendeley Data](https://data.mendeley.com/datasets/vdg2nbpc4j).

```shell
# Install dependencies
python3.8 -m pip install -r require.txt
chmod 755 discoal

# Run the 6-step pipeline
python3.8 DASD.py simu -i example/simu_config/ -o simu_data
python3.8 DASD.py calc_domain -i simu_data -o simu_feature
python3.8 DASD.py calc_target -i real_data -o real_feature
python3.8 DASD.py data_annotation -i simu_feature --config example/label_configure.txt -o trainSet
python3.8 DASD.py train \
    --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy \
    --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy \
    --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy \
    -t real_feature/ -o Ensemble_output
python3.8 DASD.py pred -m Ensemble_output_ensemble/ -M 5 -f real_feature/chr1.vcf_featureMap.npy -p real_feature/chr1.vcfposInfo -o pred_result.txt
```

Prediction currently requires `-M 5` and an ensemble directory containing exactly five sub-model directories.

## Documentation

Full documentation is available at **[docs/index.rst](docs/index.rst)** (RST / Sphinx). Build with:

```shell
python3.8 -m pip install sphinx sphinx_rtd_theme
sphinx-build -b html docs docs/_build
```

See **[Parameter_Inference.md](Parameter_Inference.md)** for guidance on estimating mutation rates, demographic history, recombination rates, and selection strength using Relate.

## Available Models

Pre-trained models for specific populations are available at [Mendeley Data](https://data.mendeley.com/datasets/vdg2nbpc4j).

| Species | Population | Location |
|---|---|---|
| *Homo sapiens* | CEU (European) | `available_models/Homo_sapiens/CEU` |
| *Sus scrofa domestica* | Large White pig | `available_models/Sus_scrofa/LW` |
| *Anopheles gambiae* | Burkina Faso | `available_models/Anopheles_gambiae/BFS` |

## References

- Song et al. (2024) — DASDC: [doi:10.1002/advs.202304842](https://doi.org/10.1002/advs.202304842)
- Kern & Schrider (2016) — discoal: [doi:10.1093/bioinformatics/btw556](https://doi.org/10.1093/bioinformatics/btw556)

## License

See [LICENSE](LICENSE) for details.
