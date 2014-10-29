import os

import click

from dad.master import run as run_master
from dad.worker import run as run_worker
from dad.worker.proc import runner


@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.option('--host', '-H', default='127.0.0.1')
@click.option('--port', '-p', default=5000)
def run(debug, host, port):
    config = {}

    if debug:
        config['DEBUG'] = True

    if host:
        os.environ['HOST'] = host

    if port:
        os.environ['PORT'] = str(port)


run.add_command(run_master, 'master')
run.add_command(run_worker, 'worker')
run.add_command(runner, 'run')
