# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst
#
# Astropy documentation build configuration file.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this file.
#
# All configuration values have a default. Some values are defined in
# the global Astropy configuration which is loaded here before anything else.
# See astropy.sphinx.conf for which values are set there.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('..'))
# IMPORTANT: the above commented section was generated by sphinx-quickstart, but
# is *NOT* appropriate for astropy or Astropy affiliated packages. It is left
# commented out with this explanation to make it clear why this should not be
# done. If the sys.path entry above is added, when the astropy.sphinx.conf
# import occurs, it will import the *source* version of astropy instead of the
# version installed (if invoked as "make html" or directly with sphinx), or the
# version in the build directory (if "python setup.py build_docs" is used).
# Thus, any C-extensions that are needed to build the documentation will *not*
# be accessible, and the documentation will not build correctly.

from datetime import datetime
import os
ON_RTD = os.environ.get('READTHEDOCS') == 'True'
ON_TRAVIS = os.environ.get('TRAVIS') == 'true'

try:
    import astropy_helpers
except ImportError:
    # Building from inside the docs/ directory?
    import os
    import sys
    if os.path.basename(os.getcwd()) == 'docs':
        a_h_path = os.path.abspath(os.path.join('..', 'astropy_helpers'))
        if os.path.isdir(a_h_path):
            sys.path.insert(1, a_h_path)

    # If that doesn't work trying to import from astropy_helpers below will
    # still blow up

# Load all of the global Astropy configuration
from astropy_helpers.sphinx.conf import *
from astropy.extern import six

import astropy

# Use the astropy style when building docs
from astropy import visualization
plot_rcparams = visualization.astropy_mpl_docs_style
plot_apply_rcparams = True
plot_html_show_source_link = False
plot_formats = ['png', 'svg', 'pdf']
# Don't use the default - which includes a numpy and matplotlib import
plot_pre_code = ""

# -- General configuration ----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.1'

# To perform a Sphinx version check that needs to be more specific than
# major.minor, call `check_sphinx_version("x.y.z")` here.
check_sphinx_version("1.2.1")

# The intersphinx_mapping in astropy_helpers.sphinx.conf refers to astropy for
# the benefit of affiliated packages who want to refer to objects in the
# astropy core.  However, we don't want to cyclically reference astropy in its
# own build so we remove it here.
del intersphinx_mapping['astropy']

# add any custom intersphinx for astropy
intersphinx_mapping['pytest'] = ('https://docs.pytest.org/en/stable/', None)
intersphinx_mapping['ipython'] = ('http://ipython.readthedocs.io/en/stable/', None)
intersphinx_mapping['pandas'] = ('http://pandas.pydata.org/pandas-docs/stable/', None)
intersphinx_mapping['sphinx_automodapi'] = ('https://sphinx-automodapi.readthedocs.io/en/stable/', None)
intersphinx_mapping['packagetemplate'] = ('http://docs.astropy.org/projects/package-template/en/latest/', None)
intersphinx_mapping['h5py'] = ('http://docs.h5py.org/en/stable/', None)

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns.append('_templates')
exclude_patterns.append('_pkgtemplate.rst')

# Add any paths that contain templates here, relative to this directory.
if 'templates_path' not in locals():  # in case parent conf.py defines it
    templates_path = []
templates_path.append('_templates')


# This is added to the end of RST files - a good place to put substitutions to
# be used globally.
rst_epilog += """
.. |minimum_numpy_version| replace:: {0.__minimum_numpy_version__}

.. Astropy
.. _Astropy: http://astropy.org
.. _`Astropy mailing list`: https://mail.python.org/mailman/listinfo/astropy
.. _`astropy-dev mailing list`: http://groups.google.com/group/astropy-dev
""".format(astropy)

# -- Project information ------------------------------------------------------

project = u'Astropy'
author = u'The Astropy Developers'
copyright = u'2011–{0}, '.format(datetime.utcnow().year) + author

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# The short X.Y version.
version = astropy.__version__.split('-', 1)[0]
# The full version, including alpha/beta/rc tags.
release = astropy.__version__


# -- Options for HTML output ---------------------------------------------------

# A NOTE ON HTML THEMES
#
# The global astropy configuration uses a custom theme,
# 'bootstrap-astropy', which is installed along with astropy. The
# theme has options for controlling the text of the logo in the upper
# left corner. This is how you would specify the options in order to
# override the theme defaults (The following options *are* the
# defaults, so we do not actually need to set them here.)

#html_theme_options = {
#    'logotext1': 'astro',  # white,  semi-bold
#    'logotext2': 'py',     # orange, light
#    'logotext3': ':docs'   # white,  light
#    }

# A different theme can be used, or other parts of this theme can be
# modified, by overriding some of the variables set in the global
# configuration. The variables set in the global configuration are
# listed below, commented out.

# Add any paths that contain custom themes here, relative to this directory.
# To use a different custom theme, add the directory containing the theme.
#html_theme_path = []

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes. To override the custom theme, set this to the
# name of a builtin theme or the name of a custom theme in html_theme_path.
#html_theme = None

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = ''

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = ''

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = '{0} v{1}'.format(project, release)

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'doc'

# A dictionary of values to pass into the template engine’s context for all pages.
html_context = {
    'to_be_indexed': ['stable', 'latest']
}

# -- Options for LaTeX output --------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [('index', project + '.tex', project + u' Documentation',
                    author, 'manual')]

latex_logo = '_static/astropy_logo.pdf'


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [('index', project.lower(), project + u' Documentation',
              [author], 1)]

# Setting this URL is requited by sphinx-astropy
github_issues_url = 'https://github.com/astropy/astropy/issues/'

# Enable nitpicky mode - which ensures that all references in the docs
# resolve.

nitpicky = True
nitpick_ignore = []

for line in open('nitpick-exceptions'):
    if line.strip() == "" or line.startswith("#"):
        continue
    dtype, target = line.split(None, 1)
    target = target.strip()
    nitpick_ignore.append((dtype, six.u(target)))

if six.PY2:
    nitpick_ignore.extend([('py:obj', six.u('bases'))])

# -- Options for the Sphinx gallery -------------------------------------------

try:
    import sphinx_gallery
    extensions += ["sphinx_gallery.gen_gallery"]

    sphinx_gallery_conf = {
        'backreferences_dir': 'generated/modules', # path to store the module using example template
        'filename_pattern': '^((?!skip_).)*$', # execute all examples except those that start with "skip_"
        'examples_dirs': '..{}examples'.format(os.sep), # path to the examples scripts
        'gallery_dirs': 'generated/examples', # path to save gallery generated examples
        'reference_url': {
            'astropy': None,
            'matplotlib': 'http://matplotlib.org/',
            'numpy': 'http://docs.scipy.org/doc/numpy/',
        },
        'abort_on_example_error': True
    }

except ImportError:
    def setup(app):
        app.warn('The sphinx_gallery extension is not installed, so the '
                 'gallery will not be built.  You will probably see '
                 'additional warnings about undefined references due '
                 'to this.')


# -- Options for linkcheck output -------------------------------------------
linkcheck_retry = 5
linkcheck_ignore = ['https://journals.aas.org/manuscript-preparation/']
linkcheck_timeout = 180
linkcheck_anchors = False

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
html_extra_path = ['robots.txt']
