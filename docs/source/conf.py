#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import abspath, dirname
from datetime import datetime
now = datetime.now()

# make sure that we're in the source directory
# so that it's consistent between read the docs and local
cur_dir = abspath(dirname(__file__))

import sanajeh

# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    ]

exclude_patterns = [
    'api/bidso.rst',
    ]

# autodoc options
autodoc_default_flags = []

# Napoleon settings
napoleon_use_rtype = False

# todo settings
todo_include_todos = True
todo_link_only = True

# source suffix
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'sanajeh'
author = "Gio Piantoni"
copyright = "2018-{}, ".format(now.year) + author

# The short X.Y version.
version = sanajeh.__version__
# The full version, including alpha/beta/rc tags.
release = version

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_show_sphinx = False
html_show_sourcelink = False

html_theme_options = {
    'collapse_navigation': False,
    'display_version': True,
    'navigation_depth': 2,
    'sticky_navigation': False,
    'prev_next_buttons_location': 'bottom',
    }

# Output file base name for HTML help builder.
htmlhelp_basename = 'sanajehdoc'
