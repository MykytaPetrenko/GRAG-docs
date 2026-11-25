# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'GRAG'
copyright = '2026, Squeezy Pixels (Mykyta Petrenko)'
author = 'Squeezy Pixels (Mykyta Petrenko)'
release = '0.9.0'

# -- General configuration ---------------------------------------------------

extensions = ['myst_parser', 'sphinx_wagtail_theme']

# Headings get anchors, so pages can link to a section such as godot.md#install.
myst_heading_anchors = 3

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_wagtail_theme'
html_title = 'GRAG Documentation'

html_theme_options = dict(
    project_name='GRAG',
    logo='img/grag_logo.svg',
    logo_alt='GRAG',
    logo_height=64,
    logo_width=64,
    logo_url='https://mykytapetrenko.github.io/GRAG-docs/',
    github_url='https://github.com/MykytaPetrenko/GRAG-docs/tree/main/docs/',
)

html_static_path = ['_static']
html_css_files = ['custom.css']
