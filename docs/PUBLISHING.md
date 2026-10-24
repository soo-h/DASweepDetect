# Publishing the documentation

The user manual is hosted at [DASDC documentation](https://dasweepdetect.readthedocs.io/en/latest/).
Readers do not need to install Sphinx or build anything.

`docs/index.rst` is the source entry point. GitHub's repository file preview
does not build the complete Sphinx site. The root `.readthedocs.yaml` selects
Ubuntu 24.04, Python 3.13, `docs/conf.py`, and the documentation dependencies in
`docs/requirements.txt`. Sphinx warnings fail the build.

## Source layout

| Source | Purpose |
|---|---|
| `docs/index.rst` | Overview, linked module table, data flow and navigation |
| `docs/installation.rst` | Environment setup and backend requirements |
| `docs/workflow/*.rst` | Six module guides with examples and parameter tables |
| `docs/parameter_inference.rst` | Canonical Relate procedure and simulation priors; replaces root `Parameter_Inference.md` |
| `docs/figure_sources.rst` | Figure attribution and adaptation details |
| `docs/outputs.rst` | Prediction columns, labels and interpretation |
| `docs/models.rst` | Population-specific trained model resources and inference |
| `docs/faq.rst` | Where to report a problem |
| `docs/README.rst` | Existing manual URL retained as an index to the new pages |
| `docs/_static/` | Local styles, diagrams, paper-derived figures and the downloadable Relate preparation script |

Use Sphinx `:doc:` and `:ref:` links between pages so that the builder can
validate references. Figures use `numfig` and `:numref:` links so captions and text references stay synchronized. The paper figure provenance is in `docs/_static/paper/sources.json`; retain its attribution when replacing images. Keep command defaults aligned with `dasdc/cli.py`.

## First build

1. Commit and push `.readthedocs.yaml`, `docs/requirements.txt`, and the Sphinx
   sources to the branch Read the Docs will build, after the changes have been
   reviewed. Select a branch that contains these files; selecting `main` before
   the documentation has been merged there will fail.
2. Import the GitHub repository `soo-h/DASweepDetect` into Read the Docs and
   select the branch containing those files. Keep the configuration file at
   the default path, `.readthedocs.yaml` in the repository root.
3. Trigger the initial build and inspect its installation and Sphinx logs.
   A successful build publishes the HTML manual at the project's documentation
   URL. Use the project's **View docs** link to confirm that the manual opens.
4. Add that public URL to the Documentation section of `README.md`.

GitHub Pages settings, a Pages deployment workflow, and a `gh-pages` branch
are not required for this hosting setup. Do not commit generated HTML.

## Subsequent updates

Edit the `.rst` files in `docs/` and submit a pull request. Relevant changes
merged into the configured branch rebuild the site through the Read the Docs
repository integration. Confirm that its webhook is connected if pushes do
not trigger builds.

Use the Read the Docs project's build controls to rebuild a version manually.
Pull-request preview builds are optional and must be enabled in the project's
settings; adding `.readthedocs.yaml` alone does not enable them.

## Optional local preview for maintainers

Use Python 3.13 to match the hosted build. Only the two documentation dependencies are needed;
there is no need to install DASDC, TensorFlow, PyTorch, or scientific datasets.
Run these commands from the repository root:

```bash
mkdir -p .tmp-docs/tmp
TMPDIR="$PWD/.tmp-docs/tmp" PYTHONDONTWRITEBYTECODE=1 \
  python3.13 -m pip install --no-cache-dir -r docs/requirements.txt
TMPDIR="$PWD/.tmp-docs/tmp" PYTHONDONTWRITEBYTECODE=1 \
  python3.13 -m sphinx -b html -n -W --keep-going docs .tmp-docs/html
python3.13 -m http.server 8000 --directory .tmp-docs/html
```

Open `http://localhost:8000/`. Build output and temporary files are under
`.tmp-docs/`, which is already ignored by Git. On a machine without the requested
locale, set `LC_ALL=C` for the build command.

The documentation can also be previewed on Windows, independently of the
Linux analysis runtime. From PowerShell in the repository root:

```powershell
py -3 -m venv .tmp-docs/venv
.\.tmp-docs\venv\Scripts\python.exe -m pip install -r docs/requirements.txt
.\.tmp-docs\venv\Scripts\python.exe -m sphinx -b html -n -W --keep-going docs docs/_build/html
.\.tmp-docs\venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory docs/_build/html
```

Review the overview's six module links, parameter tables, and output examples
in the browser before publishing. Keep generated HTML and local environments
out of commits.

If the build fails, inspect the Read the Docs build log. Check that the selected
branch contains the configuration, requirements, and Sphinx sources, and that
the dependency installation succeeded. A missing site before the first
successful build does not indicate a Sphinx source error.

See the [Read the Docs configuration reference](https://docs.readthedocs.io/en/stable/config-file/v2.html)
and [reproducible-build guide](https://docs.readthedocs.io/en/stable/guides/reproducible-builds.html).
