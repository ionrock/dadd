import os

import click

from dadd.master import run as run_master
from dadd.worker import run as run_worker
from dadd.worker.proc import runner


@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.option('--host', '-H', default='127.0.0.1')
@click.option('--port', '-p', default=5000)
@click.pass_context
def main(ctx, debug, host, port):
    ctx.obj = {}

    if debug:
        ctx.obj['DEBUG'] = 'True'

    if host:
        ctx.obj['HOST'] = host

    if port:
        ctx.obj['PORT'] = str(port)


main.add_command(run_master, 'master')
main.add_command(run_worker, 'worker')
main.add_command(runner, 'run')
