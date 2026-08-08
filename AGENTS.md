# Repository Guidelines

## Project Structure & Module Organization

`DASD.py` is the command-line entry point for the six-stage DASDC workflow. Core stages live in `DASD/`: simulation, simulated/VCF feature extraction, data labeling, DANN training, and ensemble prediction. Shared model, statistics, validation, preprocessing, and multiprocessing code belongs in `DASD/util/`. Format-specific feature routines are separated into `DASD/script_simu_fev/` and `DASD/script_real_fev/`. Example configurations and small expected prediction files are under `example/`; user documentation is in `README.md`, `Parameter_Inference.md`, and `docs/`. Treat the tracked `discoal` executable as a third-party binary, not generated source.

## Setup, Build, and Development Commands

This project targets Linux and Python 3.8 exactly; it has no separate build step.

```bash
python3.8 -m pip install -r require.txt  # install pinned runtime dependencies
chmod 755 discoal                        # enable the simulator
python3.8 DASD.py --help                 # inspect pipeline subcommands
python3.8 -m py_compile DASD.py DASD/*.py DASD/util/*.py
sphinx-build -b html docs docs/_build    # rebuild optional HTML documentation
```

Run affected stages with small inputs from `example/` before attempting full genomic datasets. See `README.md` for the complete `simu` through `pred` command sequence.

## Coding Style & Naming Conventions

Use four-space indentation and PEP 8 conventions. Prefer `snake_case` for modules, functions, variables, and new CLI options; use `PascalCase` for classes and `UPPER_CASE` for constants. Keep reusable calculations in `DASD/util/` and keep command dispatch thin. Add docstrings to public functions and comments only where scientific assumptions or array shapes are not obvious. No formatter or linter is configured, so review diffs for import hygiene, readable line lengths, and backward-compatible CLI behavior.

## Testing Guidelines

There is currently no automated test suite or coverage threshold. Every change must pass `py_compile` and a focused end-to-end smoke test of the modified stage. For numerical changes, compare shapes, labels, and representative values against known inputs; record seeds where randomness is involved. Do not silently alter source VCF, simulation, or example data. Place future regression tests in `tests/` using `test_*.py` names and document their runner.

## Commit & Pull Request Guidelines

Recent history uses short imperative subjects such as `Update DANN_train.py` and scoped fixes such as `fix(cpu): ...`. Follow that pattern: keep the first line concise, state the component, and explain scientific or behavioral consequences in the body. Pull requests should include purpose, affected pipeline stages, exact validation commands, input/output assumptions, and linked issues. Include concise before/after evidence for prediction or figure changes, but do not commit large generated datasets, models, or local cache files.
