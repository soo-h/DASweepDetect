# Repository Guidelines

## Project Structure & Module Organization

`dasdc/` provides the installed command-line interface for the six-stage workflow. TensorFlow remains the legacy training backend; `DASD/DANN_train_torch.py`, `DASD/pred_ensemble_torch.py`, and `DASD/util/torch_dann.py` implement the optional PyTorch backend. Shared statistics, validation, and preprocessing code belongs in `DASD/util/`; format-specific feature routines live in `DASD/script_simu_fev/` and `DASD/script_real_fev/`. Tests are under `tests/`, examples under `example/`, and user documentation in `README.md` and `docs/`. Treat `discoal` as a tracked third-party binary.

## Setup, Build, and Development Commands

The package syntax supports Python 3.8 or newer. TensorFlow 2.7 is limited to Python 3.8-3.9; install a CUDA-enabled PyTorch build separately for GPU training.

```bash
python -m pip install -e .               # install dependencies and the dasdc command
chmod 755 discoal                        # enable the simulator
dasdc --help                             # inspect pipeline subcommands
python -m unittest discover -s tests -v
sphinx-build -b html docs docs/_build    # rebuild optional HTML documentation
```

Run affected stages with small inputs from `example/` before attempting full genomic datasets. See `README.md` for the complete `simu` through `pred` command sequence.

## Coding Style & Naming Conventions

Use four-space indentation and PEP 8 conventions. Prefer `snake_case` for modules, functions, variables, and new CLI options; use `PascalCase` for classes and `UPPER_CASE` for constants. Keep reusable calculations in `DASD/util/` and keep command dispatch thin. Add docstrings to public functions and comments only where scientific assumptions or array shapes are not obvious. No formatter or linter is configured, so review diffs for import hygiene, readable line lengths, and backward-compatible CLI behavior.

## Testing Guidelines

Use the standard-library `unittest` suite in `tests/`; no coverage threshold is configured. Every change must pass the suite, `py_compile`, and a focused smoke test of the modified stage. For numerical changes, compare shapes, labels, and representative values against known inputs and record random seeds. Do not silently alter source VCF, simulation, or example data. Name new regression files `test_*.py`.

## Commit & Pull Request Guidelines

Recent history uses short imperative subjects such as `Update DANN_train.py` and scoped fixes such as `fix(cpu): ...`. Follow that pattern: keep the first line concise, state the component, and explain scientific or behavioral consequences in the body. Pull requests should include purpose, affected pipeline stages, exact validation commands, input/output assumptions, and linked issues. Include concise before/after evidence for prediction or figure changes, but do not commit large generated datasets, models, or local cache files.
