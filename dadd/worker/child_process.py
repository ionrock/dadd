import os
import time
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


def wait_for_path(path, timeout=5):
    """Wait for a path to exis before exiting."""
    app.logger.info('Waiting for %s' % path)
    for t in range(timeout * 10):
        if os.path.exists(path):
            return open(path).read()
        time.sleep(.1)
    return Exception('File: %s does not exist' % path)


def get_pid(env):
    path = os.path.join(env.directory, 'pid.txt')
    return int(wait_for_path(path))


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

    if not foreground:
        # Wait for the process to daemonize
        proc.wait()
        pid = get_pid(env)
    else:
        pid = proc.pid

    app.logger.info('Started: %s' % cmd)

    return {
        'spec': env.spec,
        'directory': env.directory,
        'pid': pid,
    }
