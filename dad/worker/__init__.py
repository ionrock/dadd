import os

from functools import partial

import click

from flask import Flask

from dad import server

app = Flask(__name__)
app.config.from_object('dad.worker.settings')


import dad.worker.handlers  # noqa


@click.command()
def run():
    if os.environ['DEBUG']:
        app.debug = True

    register = partial(dad.worker.handlers.register,
                       app.config['HOST'],
                       app.config['PORT'])

    server.monitor('Dad_Heartbeat', register, 2)
    server.mount(app, '/')
    server.run(app.config)
