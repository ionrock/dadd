import click

from flask import Flask, current_app
app = Flask(__name__)
app.config.from_object('dad.worker.settings')

import dad.worker.server  # noqa


@click.command()
@click.option('--port', '-p', default=6010)
def run(port):
    with app.app_context():
        dad.worker.server.register(current_app)
    app.run(port=port)
