import click

from flask import Flask

from dadd import server
from dadd.master.utils import update_config


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

    update_config(app)
    admin(app)
    server.mount(app, '/')
    server.run(app.config)
