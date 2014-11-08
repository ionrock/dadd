import os

import click
import yaml

from flask import Flask

from dadd import server

# Set up the app object before importing the handlers to avoid a
# circular import
app = Flask(__name__)
app.config.from_object('dadd.master.settings')

import dadd.master.handlers  # noqa
import dadd.master.api.procs  # noqa
import dadd.master.api.hosts  # noqa


@click.command()
def run():
    if 'DEBUG' in os.environ:
        app.debug = True

    if os.environ.get('APP_SETTINGS_YAML'):
        config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
        app.config.update(config)

    server.mount(app, '/')
    server.run(app.config)
