import os

from functools import partial

import click

from flask import Flask

from dadd import server

app = Flask(__name__)
app.config.from_object('dadd.worker.settings')


import dadd.worker.handlers  # noqa


@click.command()
@click.pass_context
def run(ctx):
    if os.environ.get('DEBUG') or (ctx.obj and ctx.obj.get('DEBUG')):
        app.debug = True

    if ctx.obj:
        app.config.update(ctx.obj)

    register = partial(dadd.worker.handlers.register,
                       app.config['HOST'],
                       app.config['PORT'])

    server.monitor('Dadd_Heartbeat', register, 2)
    server.mount(app, '/')
    server.run(app.config)
