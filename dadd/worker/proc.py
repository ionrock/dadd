import os
import sys
import json
import shutil
import tempfile
import signal
import shlex

from subprocess import Popen, call
from collections import namedtuple

import click
import daemon
import requests

from erroremail import ErrorEmail

from dadd.worker import app
from dadd.master.utils import update_config

from pprint import pprint


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


class ChildProcess(object):
    def __init__(self, spec):
        self.spec = spec
        self._info = {}

    def run(self, foreground=False):
        env = create_env(self.spec)

        cmd = [
            'dadd', 'run', env.spec,
            '--working-dir', env.directory
        ]

        if foreground:
            cmd.append('--foreground')

        self.proc = Popen(cmd)

        self._info = {
            'spec': env.spec,
            'directory': env.directory,
            'pid': self.proc.pid,
        }

    def info(self):
        return self._info


class ClientMixin(object):
    """Assuming we have an object with a spec, we provide some methods
    to talk to the master.

    Note: This should eventually be removed for an actual dadd.client"""

    def procs_url(self, tail):
        base = os.environ.get('MASTER_URL', app.config['MASTER_URL'])
        return '%s/api/procs/%s/%s' % (base, self.spec.get('process_id'), tail)

    def set_process_state(self, state):
        if 'process_id' in self.spec:
            resp = self.sess.post(self.procs_url('%s/' % state))
            if not resp.ok:
                print(resp.request.url)
                pprint(dict(resp.headers))
                print(resp.content)
                resp.raise_for_status()


class WorkerProcess(ClientMixin):

    def __init__(self, spec, sess=None):
        self.spec = spec
        self.sess = sess or requests.Session()
        # TODO: Add auth from the global config

    def setup(self):
        self.download_files()

    def start(self):
        if isinstance(self.spec['cmd'], basestring):
            parts = shlex.split(self.spec['cmd'])
        else:
            parts = self.spec['cmd']

        cmd = []
        for part in parts:
            if part == '$APP_SETTINGS':
                part = os.environ['APP_SETTINGS_JSON']
            cmd.append(part)

        print('Running: %s' % ' '.join(cmd))
        self.proc = Popen(cmd)
        self.proc.wait()

    def download_files(self):
        for filename, url in self.spec.get('download_urls', {}).iteritems():
            resp = self.sess.get(url, stream=True)
            resp.raise_for_status()

            with open(filename, 'w+') as fh:
                for chunk in resp:
                    fh.write(chunk)

    def finish(self):
        self.set_process_state('success')

    def cleanup(self, *args):
        print('Cleaning up: %s' % list(args))
        self.proc.terminate()

    @property
    def code(self):
        return self.proc.returncode


class PythonWorkerProcess(WorkerProcess):

    def create_virtualenv(self):
        call(['virtualenv', 'venv'])

    def install_python_deps(self):
        self.create_virtualenv()

        # Make sure we have a list
        if isinstance(self.spec['python_deps'], basestring):
            self.spec['python_deps'] = [self.spec['python_deps']]

        for dep in self.spec['python_deps']:
            cmd = [
                'venv/bin/pip', 'install',
            ]

            if self.spec.get('python_cheeseshop'):
                cmd.extend(['-i', self.spec['python_cheeseshop']])

            cmd.append(dep)
            print('Running: %s' % ' '.join(cmd))
            call(cmd)

    def setup(self):
        if 'python_deps' in self.spec:
            self.install_python_deps()
        self.download_files()

    def start(self):
        # Add our virtualenv to the path
        os.environ['PATH'] += ':%s' % os.path.abspath('./venv/bin/')
        super(PythonWorkerProcess, self).start()


class ErrorHandler(ClientMixin):
    def __init__(self, spec, logfile):
        self.spec = spec
        self.logfile = logfile
        self.sess = requests.Session()
        self.base_url = app.config['MASTER_URL']
        print('masterurl: %s' % self.base_url)

    def procs_url(self, tail):
        return '%s/api/procs/%s/%s' % (
            self.base_url, self.spec.get('process_id'), tail
        )

    def upload_log(self):
        if 'process_id' in self.spec:
            logfile = open(self.logfile, 'r')
            url = self.procs_url('logfile/')
            headers = {'content-type': 'text/plain'}
            self.sess.post(url, headers=headers, data=logfile)

    def send_error_email(self, *args):
        if 'ERROR_EMAIL_CONFIG' in app.config:
            mailer = ErrorEmail(app.config['ERROR_EMAIL_CONFIG'])
            message = mailer.create_message_from_traceback(args)
            mailer.send_email(message)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if None in args:
            self.set_process_state('success')
            return True

        self.upload_log()
        self.set_process_state('failed')
        self.send_error_email(*args)
        return True


@click.command()
@click.argument('specfile', type=click.File())
@click.option('--no-cleanup', is_flag=True)
@click.option('--foreground', is_flag=True)
@click.option('--working-dir', '-w')
def runner(specfile, no_cleanup, foreground, working_dir=None):
    # Make sure our config is up to date with our parent
    update_config(app)

    # Load our spec file
    spec = json.load(specfile)

    # Create a directory to work under and specify our log file.
    if not working_dir:
        env = create_env(spec)
        working_dir = env.directory
        logfile_name = env.logfile
        click.echo('Created Working Directory: %s' % env.directory)
    else:
        logfile_name = os.path.join(working_dir, 'output.log')

    # Open a file handle for logging
    if foreground:
        # If we are not daemonizing, just use stdout
        output_log = sys.stdout
    else:
        click.echo('Logging to: %s' % logfile_name)
        output_log = open(logfile_name, 'w+')

    # NOTE: Only python is supported atm
    worker = PythonWorkerProcess(spec)

    # Redirect stdout/err to our logfile and set our working directory
    daemon_conf = dict(
        stdout=output_log,
        stderr=output_log,
        working_directory=working_dir,
    )

    if foreground:
        click.echo('Running in the foreground')
        daemon_conf['detach_process'] = False

    context = daemon.DaemonContext(**daemon_conf)

    # Make sure we give our worker a chance to do clean up and notify
    # the master on any errors.
    context.signal_map.update({
        signal.SIGTERM: worker.cleanup,
    })

    error_handler = ErrorHandler(spec, logfile_name)

    with context:
        # Add our spec as an APP_SETTINGS_JSON now that we are daemonized.
        config_filename = os.path.abspath('./specfile.json')
        with open(config_filename, 'w+') as fh:
            json.dump(spec, fh)

        os.environ['APP_SETTINGS_JSON'] = config_filename

        with error_handler:
            print('Setting up')
            worker.setup()
            print('Starting')
            try:
                worker.start()
            except:
                import traceback
                traceback.print_exc()

                raise
            print('Finishing')
            worker.finish()

            if no_cleanup:
                click.echo('Not cleaning up %s' % working_dir)
            else:
                click.echo('Cleaning up the working directory: %s' % working_dir)
                shutil.rmtree(working_dir)
