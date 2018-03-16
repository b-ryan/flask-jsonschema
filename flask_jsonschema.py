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
    def __init__(self, schemas, definitions):
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
        self.app = app
        if app is not None:
            self._state = self.init_app(app)

    def init_app(self, app):
        default_dir = os.path.join(app.root_path, 'jsonschema')
        schema_dir = app.config.get('JSONSCHEMA_DIR', default_dir)
        schemas = _read_json_files(schema_dir)
        defs_dir = os.path.join(schema_dir, 'definitions')
        definitions = _read_json_files(defs_dir)
        state = _JsonSchema(schemas, definitions)
        app.extensions['jsonschema'] = state
        return state

    def validate(self, *path):
        def wrapper(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                schema = current_app.extensions['jsonschema'].get_schema(path)
                validate(request.json, schema)
                return fn(*args, **kwargs)
            return decorated
        return wrapper

    def __getattr__(self, name):
        return getattr(self._state, name, None)
