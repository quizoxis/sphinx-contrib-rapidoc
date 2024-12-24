"""
    sphinxcontrib.rapidoc
    ~~~~~~~~~~~~~~~~~~~~~

    A Sphinx extension that renders OpenAPI/Swagger specifications using RapiDoc.

    This extension allows you to:
    * Embed OpenAPI/Swagger specs in your documentation
    * Customize the RapiDoc UI appearance
    * Generate interactive API documentation

    Basic usage:
        1. Add 'sphinxcontrib.rapidoc' to your extensions in conf.py
        2. Configure the rapidoc settings in conf.py
        3. Use the ..rapidoc:: directive in your RST files

    :copyright: Copyright 2024 by QO <quiz.oxis@gmail.com>
    :license: BSD, see LICENSE for details.
"""
# Standard library imports
import os
import io
import json

# Third-party imports
import pbr.version
import jinja2
import jsonschema
import yaml
from six.moves import urllib

# Sphinx imports
from sphinx.util.fileutil import copy_asset
from sphinx.util.osutil import copyfile, ensuredir

if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa

# Version information
__version__ = pbr.version.VersionInfo('sphinxcontrib-rapidoc').version_string()

# Module constants
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
RAPIDOC_CONFIG_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'page': {'type': 'string'},
            'spec': {'type': 'string'},
            'embed': {'type': 'boolean'},
            'template': {'type': 'string'},
            'opts': {
                'type': 'object',
                'properties': {
                    'persist-auth': {'type': 'boolean'},
                    'info-description-headings-in-navbar': {'type': 'boolean'},
                    'show-header': {'type': 'boolean'},
                    'allow-authentication': {'type': 'boolean'},
                    'allow-server-selection': {'type': 'boolean'},
                    'allow-api-list-style-selection': {'type': 'boolean'},
                    'render-style': {'type': 'string'},
                    'schema-style': {'type': 'string'},
                    'allow-spec-url-load': {'type': 'boolean'},
                    'allow-spec-file-load': {'type': 'boolean'},
                    'allow-spec-file-download': {'type': 'boolean'},
                    'allow-search': {'type': 'boolean'},
                    'allow-advanced-search': {'type': 'boolean'},
                    'allow-try': {'type': 'boolean'},
                    'show-header': {'type': 'boolean'},
                    'sort-endpoints-by': {'type': 'string'},
                    'sort-tags': {'type': 'boolean'},
                    'regular-font': {'type': 'string'},
                    'font-size': {'type': 'string'},
                    'theme': {'type': 'string'},
                    'show-method-in-nav-bar': {'type': 'string'},
                    'use-path-in-nav-bar':  {'type': 'boolean'},
                    'nav-item-spacing': {'type': 'string'},
                    'nav-bg-color': {'type': 'string'},
                    'primary-color': {'type': 'string'}
                },
            },
        },
        'required': ['page', 'spec'],
        'additionalProperties': False,
    },
}


def render(app):
    """
    Render the RapiDoc template with the given app configuration.

    :param app: The Sphinx application object.
    :type app: Sphinx
    """
    try:
        # Settings set in Sphinx's conf.py may contain improper configuration
        # or typos. In order to prevent misbehaviour or failures deep down the
        # code, we want to ensure that all required settings are passed and
        # optional settings has proper type and/or value.
        jsonschema.validate(app.config.rapidoc, schema=RAPIDOC_CONFIG_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ValueError(
            'Improper configuration for sphinxcontrib-rapidoc at %s: %s' % (
                '.'.join((str(part) for part in exc.path)),
                exc.message,
            )
        )
    
    for ctx in app.config.rapidoc:
        if 'template' in ctx:
            template_path = os.path.join(app.confdir, ctx['template'])
        else:
            template_path = os.path.join(MODULE_DIR, 'rapidoc.j2')

        with io.open(template_path, encoding='utf-8') as f:
            template = jinja2.Template(f.read())
        
        # In embed mode, we are going to embed the whole OpenAPI spec into
        # produced HTML. The rationale is very simple: we want to produce
        # browsable HTMLs ready to be used without any web server.
        if ctx.get('embed') is True:
            # Parse & dump the spec to have it as properly formatted json
            specfile = os.path.join(app.confdir, ctx['spec'])
            with io.open(specfile, encoding='utf-8') as specfp:
                try:
                    spec_contents = yaml.safe_load(specfp)
                except ValueError as ver:
                    raise ValueError('Cannot parse spec %r: %s'
                                     % (ctx['spec'], ver))

                ctx['spec'] = json.dumps(spec_contents)
        
        # The 'spec' may contain either HTTP(s) link or filesystem path. In
        # case of later we need to copy the spec into output directory, as
        # otherwise it won't be available when the result is deployed.
        elif not ctx['spec'].startswith(('http', 'https')):

            specpath = os.path.join(app.builder.outdir, '_specs')
            specname = os.path.basename(ctx['spec'])

            ensuredir(specpath)

            copyfile(
                # Since the path may be relative it should be joined with
                # base URI which is a path of directory with conf.py in
                # our case.
                os.path.join(app.confdir, ctx['spec']),
                os.path.join(specpath, specname))
            
            # The link inside the rendered document must refer to a new
            # location, the place where it has been copied to.
            ctx['spec'] = os.path.join('_specs', specname)
        
        # Propagate information about page rendering to Sphinx. There's
        # a little trick in here: we pass an actual Jinja2 template instance
        # instead of template name. This is passible due to Jinja2 API where
        # we can pass a template instance to Jinja2 environment and so on.
        # Such little trick allows us to avoid other hacks which require
        # manipulating of Sphinx's 'templates_path' option.
        ctx.setdefault('opts', {})
        yield ctx['page'], ctx, template


def assets(app, exception):
    """
    Handle the copying of RapiDoc assets to the Sphinx output directory.

    This function ensures that the '_static' directory exists and copies the
    RapiDoc JavaScript file to it. If a custom RapiDoc URI is specified in the
    Sphinx configuration, it retrieves the RapiDoc bundle from the specified URI.

    :param app: The Sphinx application object.
    :type app: Sphinx
    :param exception: The exception object if an exception occurred during the build process.
    :type exception: Exception or None
    """
    if not exception:
        copy_asset(
            os.path.join(MODULE_DIR, 'rapidoc.js'),
            os.path.join(app.builder.outdir, '_static'))

        # It's hard to keep up with RapiDoc releases, especially when you don't
        # watch them closely. Hence, there should be a way to override built-in
        # RapiDoc bundle with some upstream one.
        if app.config.rapidoc_uri:
            urllib.request.urlretrieve(
                app.config.rapidoc_uri,
                os.path.join(app.builder.outdir, '_static', 'rapidoc.js'))

def setup(app):
    """
    Set up the Sphinx extension.

    This function is required by Sphinx to initialize the extension. It connects
    the necessary events and configuration values to the Sphinx application.

    :param app: The Sphinx application object.
    :type app: Sphinx
    :return: A dictionary with metadata about the extension.
    :rtype: dict
    """
    app.add_config_value('rapidoc', [], 'html')
    app.add_config_value('rapidoc_uri', None, 'html')
    app.connect('html-collect-pages', render)
    app.connect('build-finished', assets)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
