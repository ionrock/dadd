from functools import partial

import click

from flask import Flask

from dad import server

app = Flask(__name__)
app.config.from_object('dad.worker.settings')

# if os.environ.get('APP_SETTINGS_YAML'):
#     config = yaml.safe_load(open(os.environ['APP_SETTINGS_YAML']))
#     app.config.update(config)


import dad.worker.handlers  # noqa


@click.command()
@click.option('--host', '-H', default='127.0.0.1')
@click.option('--port', '-p', default=6010)
def run(host, port):
    if host:
        app.config['HOST'] = host

    if port:
        app.config['PORT'] = port

    register = partial(dad.worker.handlers.register, host, port)

    server.monitor('dad_heart_beat', register, 15)

    server.mount(app, '/')
    server.run(app.config)
