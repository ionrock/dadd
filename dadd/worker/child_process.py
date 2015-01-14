import os
import json
import tempfile
import subprocess

from collections import namedtuple
from dadd.worker import app


ProcessEnv = namedtuple('ProcessEnv', [
    'spec',
    'directory',
    'logfile'
])


def create_env(spec):
    tempdir = tempfile.mkdtemp()
    spec_filename = os.path.join(tempdir, 'spec.json')

    with open(spec_filename, 'w+') as fh:
        json.dump(spec, fh)

    return ProcessEnv(
        spec_filename, tempdir, os.path.join(tempdir, 'output.log')
    )


def start(spec, foreground=False):
    env = create_env(spec)

    cmd = [
        'dadd', 'run',
        '--working-dir', env.directory
    ]

    if foreground:
        cmd.append('--foreground')

    cmd.append(env.spec)

    proc = subprocess.Popen(cmd,
                            stderr=subprocess.STDOUT,
                            close_fds=True)
    proc.wait()
    pid = proc.pid
    app.logger.info('Started: %s' % cmd)

    return {
        'spec': env.spec,
        'directory': env.directory,
        'pid': pid,
    }
