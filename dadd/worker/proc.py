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
            '--working-dir', env.directory,
            '--cleanup-working-dir'
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


class WorkerProcess(object):

    def __init__(self, spec, sess=None):
        self.spec = spec
        self.sess = sess or requests.Session()
        # TODO: Add auth from the global config

    def setup(self):
        self.download_files()

    def start(self):
        raise NotImplementedError()

    def download_files(self):
        for filename, url in self.spec.get('download_urls', {}).iteritems():
            resp = self.sess.get(url, stream=True)
            resp.raise_for_status()

            with open(filename, 'w+') as fh:
                for chunk in resp:
                    fh.write(chunk)


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
        cmd = shlex.split(self.spec['cmd'])

        # Use the virtulaenv python
        if cmd[0].startswith('python'):
            cmd[0] = 'venv/bin/%s' % cmd[0]

        print('Running: %s' % cmd)
        self.proc = Popen(cmd)
        self.proc.wait()

    @property
    def code(self):
        return self.proc.returncode

    def cleanup(self, *args):
        print('Cleaning up: %s' % list(args))
        self.proc.terminate()

    def finish(self):
        print('notifying master...')


class ErrorHandler(object):
    def __init__(self, spec, logfile):
        self.spec = spec
        self.logfile = logfile
        self.sess = requests.Session()

    def procs_url(self, tail):
        base = app.config['MASTER_URL']
        return '%s/api/procs/%s/%s' % (base, self.spec.get('process_id'), tail)

    def upload_log(self):
        if 'process_id' in self.spec:
            logfile = open(self.logfile, 'r')
            url = self.procs_url('logfile/')
            headers = {'content-type': 'text/plain'}
            self.sess.post(url, headers=headers, data=logfile)

    def set_process_state(self, state):
        if 'process_id' in self.spec:
            try:
                self.sess.post(self.procs_url('%s/' % state))
            except requests.exceptions.ConnectionError:
                # TODO: Display a warning.
                pass

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
@click.option('--cleanup-working-dir', is_flag=True)
@click.option('--foreground', is_flag=True)
@click.option('--working-dir', '-w')
def runner(specfile, cleanup_working_dir, foreground, working_dir=None):
    # Load our spec file
    spec = json.load(specfile)
    click.echo('Got config: %s' % spec)

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

    with context:
        # Add our spec as an APP_SETTINGS_JSON now that we are daemonized.
        os.environ['APP_SETTINGS_JSON'] = specfile.name

        with ErrorHandler(spec, logfile_name):
            print('Setting up')
            worker.setup()
            print('Starting')
            worker.start()
            print('Finishing')
            worker.finish()

        if cleanup_working_dir:
            click.echo('Cleaning up the working directory: %s' % working_dir)
            shutil.rmtree(working_dir)