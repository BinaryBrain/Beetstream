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

"""Beetstream is a Beets.io plugin that exposes SubSonic API endpoints."""
from beets.plugins import BeetsPlugin
from beets import config
from beets import ui
import flask
from flask import g
from flask_cors import CORS

ARTIST_ID_PREFIX = "1"
ALBUM_ID_PREFIX = "2"
SONG_ID_PREFIX = "3"

# Flask setup.
app = flask.Flask(__name__)

@app.before_request
def before_request():
    g.lib = app.config['lib']

@app.route('/')
def home():
    return "Beetstream server running"

from beetsplug.beetstream.utils import *
import beetsplug.beetstream.albums
import beetsplug.beetstream.artists
import beetsplug.beetstream.dummy
import beetsplug.beetstream.playlists
import beetsplug.beetstream.search
import beetsplug.beetstream.songs
import beetsplug.beetstream.users

# Plugin hook.
class BeetstreamPlugin(BeetsPlugin):
    def __init__(self):
        super(BeetstreamPlugin, self).__init__()
        self.config.add({
            'host': u'0.0.0.0',
            'port': 8080,
            'cors': '*',
            'cors_supports_credentials': True,
            'reverse_proxy': False,
            'include_paths': False,
            'never_transcode': False,
            'playlist_dir': '',
        })

    def commands(self):
        cmd = ui.Subcommand('beetstream', help=u'run Beetstream server, exposing SubSonic API')
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
            app.config['never_transcode'] = self.config['never_transcode']
            playlist_dir = self.config['playlist_dir']
            if not playlist_dir:
                playlist_dir = config['smartplaylist']['playlist_dir'].get()
            app.config['playlist_dir'] = playlist_dir

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
