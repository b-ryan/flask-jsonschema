Flask-JsonSchema
================

This repository is forked from the
[original](https://github.com/mattupstate/flask-jsonschema) in order to support
JSON Schema References (additionally because the original has not been updated
in nearly 5 years). See documentation below.

Differences from the original

* Support for JSON Schema References
* Any changes to this repository will *officially* only support Python 3. The
  library is so small it might just end up supporting Python 2 anyway though.
* Support for auto-reloading schemas


Installation
------------

With pip::

    pip install git+https://github.com/b-ryan/flask-jsonschema.git@master


If this gains any amount of popularity I can make a PyPi package for it.

Usage
-----

JSON request validation for Flask applications.

Place schemas in the specified ``JSONSCHEMA_DIR``. ::

    import os

    from flask import Flask, request
    from flask_jsonschema import JsonSchema, ValidationError

    app = Flask(__name__)
    app.config['JSONSCHEMA_DIR'] = os.path.join(app.root_path, 'schemas')

    jsonschema = JsonSchema(app)

    @app.errorhandler(ValidationError)
    def on_validation_error(e):
        return "error"

    @app.route('/books', methods=['POST'])
    @jsonschema.validate('books', 'create')
    def create_book():
        # create the book
        return 'success'

The schema for the example above should be named ``books.json`` and should
reside in the configured folder. It should look like so::

    {
      "create": {
        "type": "object",
        "properties": {
          "title": {},
          "author": {}
        },
        "required": ["title", "author"]
      },
      "update": {
        "type": "object",
        "properties": {
          "title": {},
          "author": {}
        }
      }
    }

Notice the top level action names. Flask-JsonSchema supports one "path" level so
that you can organize related schemas in one file. If you do not wish to use this
feature you can simply use one schema per file and remove the second parameter
to the ``@jsonschema.validate`` call.

JSON Schema References
----------------------

Sometimes you may want to DRY up your schemas and put commonly-used schemas in
a central location. You can do this by creating a ``definitions`` directory
within your ``schemas`` directory. Each JSON file in this directory may contain
a single schema that will then be made available to each of your top-level
schemas. For example, you may have a file named ``definitions/author.json``
with contents::

    {
      "type": "string"
    }

And then modify the above example schema file to look like this::

    {
      "create": {
        "type": "object",
        "properties": {
          "title": {},
          "author": {"$ref": "#/definitions/author"}
        },
        "required": ["title", "author"]
      },
      "update": {
        "type": "object",
        "properties": {
          "title": {},
          "author": {"$ref": "#/definitions/author"}
        }
      }
    }

Resources
---------

- `Issue Tracker <http://github.com/b-ryan/flask-jsonschema/issues>`_
- `Code <http://github.com/b-ryan/flask-jsonschema/>`_
