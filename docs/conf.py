# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'DASDC'
copyright = '2024, DASDC Authors'
author = 'DASDC Authors'

# The full version, including alpha/beta/rc tags
release = '1.0.1'
version = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

# The master toctree document.
master_doc = 'index'

# Number figures and resolve :numref: links in the manual.
numfig = True
numfig_secnum_depth = 0
numfig_format = {'figure': 'Fig. %s', 'table': 'Table %s', 'code-block': 'Listing %s'}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets).
html_static_path = ['_static']
html_css_files = ['custom.css']
html_title = 'DASDC documentation'
html_short_title = 'DASDC'
html_theme_options = {
    'collapse_navigation': False,
    'navigation_depth': 2,
    'titles_only': False,
}

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'DASDCdoc'

# -- Options for manual page output ------------------------------------------

# One entry per manual page.
man_pages = [
    (master_doc, 'dasdc', 'DASDC Documentation',
     [author], 1)
]
