import os


project = 'sphinxcontrib-rapidoc'
copyright = '2024, QO'
author = 'QO'
version = '1.0'
release = '1.0.1b'

source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'

extlinks = {
    'issue': ('https://github.com/quizoxis/sphinx-contrib-rapidoc/issues/%s', '#'),
    'pr': ('https://github.com/quizoxis/sphinx-contrib-rapidoc/pulls/%s', 'PR #'),
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.extlinks', 'sphinxcontrib.rapidoc']

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# rapidoc_uri = 'https://cdn.jsdelivr.net/npm/rapidoc@latest/dist/rapidoc-min.js'

rapidoc = [
    {
        'name': 'Github API (v3)',
        'page': 'api/github/index',
        'spec': '_specs/github.yml',
        'embed': False,
        'opts': {
          'persist-auth':False,
          'info-description-headings-in-navbar':True,
          'show-header':False,
          'allow-authentication':True,
          'allow-server-selection':False,
          'allow-api-list-style-selection':True,
          'render-style':'read',
          'schema-style':'table',
          'allow-spec-url-load':False,
          'allow-spec-file-load':False,
          'allow-spec-file-download':False,
          'allow-search':True,
          'allow-advanced-search':True,
          'allow-try':True,
          'show-header':False,
          'sort-endpoints-by':'path',
          'sort-tags':True,
          'regular-font':'proxima-nova,Arial,Helvetica,sans-serif',
          'font-size':'default',
          'theme':'light',
          'show-method-in-nav-bar':'as-colored-block',
          'use-path-in-nav-bar':True,
          'nav-item-spacing':'compact',
          'nav-bg-color':'#3f4d67',
          'primary-color':'#5c7096',  
        },
    },
]
