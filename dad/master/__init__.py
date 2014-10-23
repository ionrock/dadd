import os

import click
import yaml

from flask import Flask

# Set up the app object before importing the handlers to avoid a
# circular import
app = Flask(__name__)

app.config.from_object('dad.master.settings')

if os.environ.get('APP_SETTINGS_YAML'):
    config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
    app.config.update(config)


import dad.master.server  # noqa


@click.command()
@click.option('--port', '-p', default=5000)
def run(port):
    app.run(port=port)
