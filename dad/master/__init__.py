import os

import click
import yaml

from flask import Flask

from dad import server

# Set up the app object before importing the handlers to avoid a
# circular import
app = Flask(__name__)

app.config.from_object('dad.master.settings')

if os.environ.get('APP_SETTINGS_YAML'):
    config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
    app.config.update(config)


import dad.master.handlers  # noqa
import dad.master.api.procs  # noqa
import dad.master.api.hosts  # noqa


@click.command()
@click.option('--host', '-H', default='127.0.0.1')
@click.option('--port', '-p', default=5000)
def run(host, port):
    if host:
        app.config['HOST'] = host

    if port:
        app.config['PORT'] = port

    server.mount(app, '/')
    server.run(app.config)
