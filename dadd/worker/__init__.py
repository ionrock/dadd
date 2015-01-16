from functools import partial

import click

from flask import Flask

from dadd import server
from dadd.master.utils import update_config

app = Flask(__name__)
app.config.from_object('dadd.worker.settings')


import dadd.worker.handlers  # noqa
from dadd.worker.utils import get_hostname


@click.command()
@click.pass_context
def run(ctx):
    if ctx.obj:
        app.config.update(ctx.obj)

    update_config(app)

    register = partial(dadd.worker.handlers.register,
                       app,
                       app.config['PORT'],
                       hostname=get_hostname(app))

    # Log the hostname:port we are registering with the master.
    app.logger.info('Registering %s:%s with master.' % (
        get_hostname(app), app.config['PORT']))

    server.monitor('Dadd_Heartbeat', register, 2)
    server.mount(app, '/')
    server.run(app.config)
