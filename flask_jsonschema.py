# -*- coding: utf-8 -*-
"""
    flask_jsonschema
    ~~~~~~~~~~~~~~~~

    flask_jsonschema
"""

import os

from functools import wraps

try:
    import simplejson as json
except ImportError:
    import json

from flask import current_app, request
from jsonschema import ValidationError, validate


class _JsonSchema(object):
    def __init__(self, app):
        self._app = app
        self._schemas = None
        self._defs = None
        self.read()

    def read(self):
        default_dir = os.path.join(self._app.root_path, 'jsonschema')
        schema_dir = self._app.config.get('JSONSCHEMA_DIR', default_dir)
        schemas = _read_json_files(schema_dir)
        defs_dir = os.path.join(schema_dir, 'definitions')
        definitions = _read_json_files(defs_dir)
        self._schemas = schemas
        self._defs = definitions

    def get_schema(self, path):
        rv = self._schemas[path[0]]
        for p in path[1:]:
            rv = rv[p]
        rv['definitions'] = self._defs
        return rv


def _json_files(directory):
    all_ = [os.path.join(directory, path) for path in os.listdir(directory)]
    return [f for f in all_ if not os.path.isdir(f) and f.endswith('.json')]


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _read_json_files(directory):
    files = _json_files(directory) if os.path.isdir(directory) else []
    return {
        os.path.basename(f).split('.')[0]: _read_json(f)
        for f in files
    }


class JsonSchema(object):
    def __init__(self, app=None):
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self._state = _JsonSchema(app)
        app.extensions['jsonschema'] = self._state
        return self._state

    def validate(self, *path):
        def wrapper(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if self.app.config.get('DEBUG'):
                    self._state.read()
                schema = self._state.get_schema(path)
                validate(request.json, schema)
                return fn(*args, **kwargs)
            return decorated
        return wrapper

    def __getattr__(self, name):
        return getattr(self._state, name, None)
