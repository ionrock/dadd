import os

import yaml
import click

from flask import Flask
from flask.ext.admin import Admin

from dadd import server


# Set up the app object before importing the handlers to avoid a
# circular import
app = Flask(__name__)
app.config.from_object('dadd.master.settings')

import dadd.master.handlers  # noqa
import dadd.master.api.procs  # noqa
import dadd.master.api.hosts  # noqa
from dadd.master.admin import admin


@click.command(name='master')
@click.pass_context
def run(ctx):
    if ctx.obj:
        app.config.update(ctx.obj)

    if 'DEBUG' in os.environ:
        app.debug = True

    if os.environ.get('APP_SETTINGS_YAML'):
        config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
        app.config.update(config)

    admin(app)
    server.mount(app, '/')
    server.run(app.config)
