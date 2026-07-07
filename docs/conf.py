# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from datetime import datetime, timezone

project = 'sqlalchemyseed'
author = 'jedymatt'
copyright = f'2022–{datetime.now(timezone.utc):%Y}, {author}'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.intersphinx',
    'autoapi.extension',
    'sphinx_copybutton',
]

templates_path = ['_templates']

# Patterns, relative to the source directory, to ignore when looking for source
# files. Also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
#
# Lets cross-references such as :class:`~sqlalchemy.ext.asyncio.AsyncSession`
# resolve to the upstream documentation instead of rendering as dead text.

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
}


# -- Options for AutoAPI -----------------------------------------------------
# https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html
#
# AutoAPI reads the source tree statically, so the package does not need to be
# importable (or its runtime dependencies installed) to build the docs.

autoapi_dirs = ['../src']
autoapi_options = ['members', 'undoc-members', 'show-inheritance']
autoapi_member_order = 'groupwise'
# Keep the generated API pages under /api/ (AutoAPI defaults to /autoapi/);
# changing this would break existing inbound links.
autoapi_root = 'api'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
