# Publishing the documentation

The user manual is built and hosted by [Read the Docs](https://readthedocs.org/).
Readers do not need to install Sphinx or build anything. The public URL is
assigned when the project is imported; copy the actual URL into `README.md`
after the first successful build.

`docs/index.rst` is the source entry point. GitHub's repository file preview
does not build the complete Sphinx site. The root `.readthedocs.yaml` selects
Ubuntu 24.04, Python 3.13, `docs/conf.py`, and the documentation dependencies in
`docs/requirements.txt`. Sphinx warnings fail the build.

## First build

1. Commit and push `.readthedocs.yaml`, `docs/requirements.txt`, and the Sphinx
   sources to the branch Read the Docs will build. The intended default is
   `main`, so merge the feature branch before selecting `main` for the build.
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
  python3.13 -m sphinx -b html -W --keep-going docs .tmp-docs/html
python3.13 -m http.server 8000 --directory .tmp-docs/html
```

Open `http://localhost:8000/`. Build output and temporary files are under
`.tmp-docs/`, which is already ignored by Git. On a machine without the requested
locale, set `LC_ALL=C` for the build command.

If the build fails, inspect the Read the Docs build log. Check that the selected
branch contains the configuration, requirements, and Sphinx sources, and that
the dependency installation succeeded. A missing site before the first
successful build does not indicate a Sphinx source error.

See the [Read the Docs configuration reference](https://docs.readthedocs.io/en/stable/config-file/v2.html)
and [reproducible-build guide](https://docs.readthedocs.io/en/stable/guides/reproducible-builds.html).
