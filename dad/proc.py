import os
import json
import shutil
import tempfile

from subprocess import Popen, call

import click
import daemon
import requests


class ChildProcess(object):
    daemon = True

    def __init__(self, spec):
        self.spec = spec
        self._info = {}

    def run(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            json.dump(self.spec, fh)
            self.proc = Popen(['dad-runner', fh.name])
            self._info = {'pid': self.proc.pid}

    def info(self):
        return self._info


class WorkerProcess(object):

    def __init__(self, spec):
        self.spec = spec
        self.sess = requests.Session()
        # TODO: Add auth from the global config

    def setup(self):
        self.download_files()

    def start(self):
        raise NotImplementedError()

    def download_files(self):
        for filename, url in self.spec.get('download_urls').iteritems():
            resp = self.sess.get(url, stream=True)
            resp.raise_for_status()

            with open(filename, 'w+') as fh:
                for chunk in resp:
                    fh.write(chunk)


class PythonWorkerProcess(WorkerProcess):

    def create_virtualenv(self):
        call(['virtualenv', 'venv'])

    def setup(self):
        if 'python_deps' in self.spec:
            self.create_virtualenv()

            for dep in self.spec['python_deps']:
                call([
                    'venv/bin/pip', 'install',
                    '-i', 'http://cheese.yougov.net', dep
                ])
        self.download_files()

    def start(self):
        # TODO: Use shlex
        cmd = self.spec['cmd'].split()

        # Use the virtulaenv python
        if cmd[0].startswith('python'):
            cmd[0] = 'venv/bin/' % cmd[0]

        self.code = call(cmd)


@click.command()
# @click.argument('global_config', type=click.File())
@click.argument('proc_config', type=click.File())
def runner(proc_config):
    spec = json.load(proc_config)
    click.echo('Got config: %s' % spec)

    tempdir = tempfile.mkdtemp()
    click.echo('Working in: %s' % tempdir)
    logfile = os.path.join(tempdir, 'output.log')
    click.echo('Logfile: %s' % logfile)

    output_log = open(logfile, 'w+')

    daemon_context = {
        'stdout': output_log,
        'stderr': output_log,
        'working_directory': tempdir,
    }

    # TODO: Only python is supported atm
    worker = PythonWorkerProcess(spec)

    # TODO: Redirect output and handle errors
    with daemon.DaemonContext(**daemon_context):
        worker.setup()
        worker.start()
        if not worker.code:
            shutil.rmtree(tempdir)
