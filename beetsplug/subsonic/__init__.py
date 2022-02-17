# -*- coding: utf-8 -*-
# This file is part of beets.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Beets.io plugin that exposes SubSonic API endpoints."""
from beets.plugins import BeetsPlugin
from beets import ui
from beets import util
import beets.library
import flask
from flask import g, jsonify, request, Response
from werkzeug.routing import BaseConverter, PathConverter
import os
from unidecode import unidecode
import json
import base64
from beets.random import random_objs
import xml.etree.cElementTree as ET
from math import ceil
from flask_cors import CORS

ARTIST_ID_PREFIX = "1"
ALBUM_ID_PREFIX = "2"
SONG_ID_PREFIX = "3"

# Flask setup.
app = flask.Flask(__name__)

class IdListConverter(BaseConverter):
    """Converts comma separated lists of ids in urls to integer lists.
    """

    def to_python(self, value):
        ids = []
        for id in value.split(','):
            try:
                ids.append(int(id))
            except ValueError:
                pass
        return ids

    def to_url(self, value):
        return ','.join(str(v) for v in value)

class QueryConverter(PathConverter):
    """Converts slash separated lists of queries in the url to string list.
    """

    def to_python(self, value):
        queries = value.split('/')
        return [query.replace('\\', os.sep) for query in queries]

    def to_url(self, value):
        return ','.join([v.replace(os.sep, '\\') for v in value])


class EverythingConverter(PathConverter):
    regex = '.*?'

app.url_map.converters['idlist'] = IdListConverter
app.url_map.converters['query'] = QueryConverter
app.url_map.converters['everything'] = EverythingConverter


@app.before_request
def before_request():
    g.lib = app.config['lib']

@app.route('/')
def home():
    return "Beets-SubSonic-API running"

from beetsplug.subsonic.utils import *
import beetsplug.subsonic.songs
import beetsplug.subsonic.search
import beetsplug.subsonic.albums
import beetsplug.subsonic.artists
import beetsplug.subsonic.users

def _rep(obj, expand=False):
    """Get a flat -- i.e., JSON-ish -- representation of a beets Item or
    Album object. For Albums, `expand` dictates whether tracks are
    included.
    """
    out = dict(obj)

    if isinstance(obj, beets.library.Item):
        if app.config.get('INCLUDE_PATHS', False):
            out['path'] = util.displayable_path(out['path'])
        else:
            del out['path']

        # Filter all bytes attributes and convert them to strings.
        for key, value in out.items():
            if isinstance(out[key], bytes):
                out[key] = base64.b64encode(value).decode('ascii')

        # Get the size (in bytes) of the backing file. This is useful
        # for the Tomahawk resolver API.
        try:
            out['size'] = os.path.getsize(util.syspath(obj.path))
        except OSError:
            out['size'] = 0

        return out

    elif isinstance(obj, beets.library.Album):
        del out['artpath']
        if expand:
            out['items'] = [_rep(item) for item in obj.items()]
        return out


def json_generator(items, root, expand=False):
    """Generator that dumps list of beets Items or Albums as JSON

    :param root:  root key for JSON
    :param items: list of :class:`Item` or :class:`Album` to dump
    :param expand: If true every :class:`Album` contains its items in the json
                   representation
    :returns:     generator that yields strings
    """
    yield '{"%s":[' % root
    first = True
    for item in items:
        if first:
            first = False
        else:
            yield ','
        yield json.dumps(_rep(item, expand=expand))
    yield ']}'


def is_expand():
    """Returns whether the current request is for an expanded response."""

    return flask.request.values.get('expand') is not None


def is_delete():
    """Returns whether the current delete request should remove the selected
    files.
    """

    return flask.request.values.get('delete') is not None


def get_method():
    """Returns the HTTP method of the current request."""
    return flask.request.method


def resource(name, patchable=False):
    """Decorates a function to handle RESTful HTTP requests for a resource.
    """
    def make_responder(retriever):
        def responder(ids):
            entities = [retriever(id) for id in ids]
            entities = [entity for entity in entities if entity]

            if get_method() == "DELETE":
                for entity in entities:
                    entity.remove(delete=is_delete())

                return flask.make_response(jsonify({'deleted': True}), 200)

            elif get_method() == "PATCH" and patchable:
                for entity in entities:
                    entity.update(flask.request.get_json())
                    entity.try_sync(True, False)  # write, don't move

                if len(entities) == 1:
                    return jsonpify(request, _rep(entities[0], expand=is_expand()))
                elif entities:
                    return app.response_class(
                        json_generator(entities, root=name),
                        mimetype='application/json'
                    )

            elif get_method() == "GET":
                if len(entities) == 1:
                    return jsonpify(request, _rep(entities[0], expand=is_expand()))
                elif entities:
                    return app.response_class(
                        json_generator(entities, root=name),
                        mimetype='application/json'
                    )
                else:
                    return flask.abort(404)

            else:
                return flask.abort(405)

        responder.__name__ = 'get_{0}'.format(name)

        return responder
    return make_responder


def resource_query(name, patchable=False):
    """Decorates a function to handle RESTful HTTP queries for resources.
    """
    def make_responder(query_func):
        def responder(queries):
            entities = query_func(queries)

            if get_method() == "DELETE":
                for entity in entities:
                    entity.remove(delete=is_delete())

                return flask.make_response(jsonify({'deleted': True}), 200)

            elif get_method() == "PATCH" and patchable:
                for entity in entities:
                    entity.update(flask.request.get_json())
                    entity.try_sync(True, False)  # write, don't move

                return app.response_class(
                    json_generator(entities, root=name),
                    mimetype='application/json'
                )

            elif get_method() == "GET":
                return app.response_class(
                    json_generator(
                        entities,
                        root='results', expand=is_expand()
                    ),
                    mimetype='application/json'
                )

            else:
                return flask.abort(405)

        responder.__name__ = 'query_{0}'.format(name)

        return responder

    return make_responder


def resource_list(name):
    """Decorates a function to handle RESTful HTTP request for a list of
    resources.
    """
    def make_responder(list_all):
        def responder():
            return app.response_class(
                json_generator(list_all(), root=name, expand=is_expand()),
                mimetype='application/json'
            )
        responder.__name__ = 'all_{0}'.format(name)
        return responder
    return make_responder


def _get_unique_table_field_values(model, field, sort_field):
    """ retrieve all unique values belonging to a key from a model """
    if field not in model.all_keys() or sort_field not in model.all_keys():
        raise KeyError
    with g.lib.transaction() as tx:
        rows = tx.query('SELECT DISTINCT "{0}" FROM "{1}" ORDER BY "{2}"'
                        .format(field, model._table, sort_field))
    return [row[0] for row in rows]

# Plugin hook.
class SubSonicPlugin(BeetsPlugin):
    def __init__(self):
        super(SubSonicPlugin, self).__init__()
        self.config.add({
            'host': u'127.0.0.1',
            'port': 8080,
            'cors': '*',
            'cors_supports_credentials': True,
            'reverse_proxy': False,
            'include_paths': False,
        })

    def commands(self):
        cmd = ui.Subcommand('subsonic', help=u'expose a SubSonic API')
        cmd.parser.add_option(u'-d', u'--debug', action='store_true',
                              default=False, help=u'debug mode')

        def func(lib, opts, args):
            args = ui.decargs(args)
            if args:
                self.config['host'] = args.pop(0)
            if args:
                self.config['port'] = int(args.pop(0))

            app.config['lib'] = lib
            # Normalizes json output
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

            app.config['INCLUDE_PATHS'] = self.config['include_paths']

            # Enable CORS if required.
            if self.config['cors']:
                self._log.info(u'Enabling CORS with origin: {0}',
                               self.config['cors'])
                app.config['CORS_ALLOW_HEADERS'] = "Content-Type"
                app.config['CORS_RESOURCES'] = {
                    r"/*": {"origins": self.config['cors'].get(str)}
                }
                CORS(
                    app,
                    supports_credentials=self.config[
                        'cors_supports_credentials'
                    ].get(bool)
                )

            # Allow serving behind a reverse proxy
            if self.config['reverse_proxy']:
                app.wsgi_app = ReverseProxied(app.wsgi_app)

            # Start the web application.
            app.run(host=self.config['host'].as_str(),
                    port=self.config['port'].get(int),
                    debug=opts.debug, threaded=True)
        cmd.func = func
        return [cmd]

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    From: http://flask.pocoo.org/snippets/35/

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)
